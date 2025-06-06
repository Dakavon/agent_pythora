# ------------------------------------------------------------------------------
#
#   Copyright 2023 eightballer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains a scaffold of a handler."""

import json
from typing import Any, SupportsFloat, cast

from aea.skills.base import Handler
from aea.protocols.base import Message

from packages.eightballer.protocols.http.message import HttpMessage
from packages.eightballer.skills.prometheus.dialogues import (
    HttpDialogue,
    HttpDialogues,
    PrometheusDialogue,
    PrometheusDialogues,
)
from packages.eightballer.protocols.prometheus.message import PrometheusMessage


class PrometheusHandler(Handler):
    """This class handles responses from the prometheus server."""

    SUPPORTED_PROTOCOL = PrometheusMessage.protocol_id

    def setup(self) -> None:
        """Set up the handler."""
        self.context.logger.info("setting up PrometheusHandler")

    def handle(self, message: Message) -> None:
        """Implement the reaction to a message."""
        message = cast(PrometheusMessage, message)

        # recover dialogue
        prometheus_dialogues = cast(PrometheusDialogues, self.context.prometheus_dialogues)
        prometheus_dialogue = cast(PrometheusDialogue, prometheus_dialogues.update(message))
        if prometheus_dialogue is None:
            self._handle_unidentified_dialogue(message)
            return

        if message.performative == PrometheusMessage.Performative.RESPONSE:
            self.context.logger.debug(f"Prometheus response ({message.code}): {message.message}")
        else:  # pragma: nocover
            self.context.logger.debug(
                f"got unexpected prometheus message: Performative = {PrometheusMessage.Performative}"
            )

    def _handle_unidentified_dialogue(self, msg: Message) -> None:
        """Handle an unidentified dialogue."""

        self.context.logger.info(f"received invalid message={msg}, unidentified dialogue.")

    def teardown(self) -> None:
        """Teardown the handler."""


def find(dotted_path: str, data: dict[str, Any]) -> Any | None:
    """Find entry at dotted_path in data."""

    keys = dotted_path.split(".")
    value = data
    for key in keys:
        value = value.get(key, {})
    return None if value == {} else value


def is_number(value: SupportsFloat) -> bool:
    """Test if value is a number."""
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


class HttpHandler(Handler):
    """This class provides a simple http handler."""

    SUPPORTED_PROTOCOL = HttpMessage.protocol_id

    def __init__(self, **kwargs: Any):
        """Initialize the handler."""
        super().__init__(**kwargs)

        self._http_server_id = None  # type: Optional[str]

    def setup(self) -> None:
        """Set up the handler."""
        self.context.logger.info("setting up HttpHandler")

    def handle(self, message: Message) -> None:
        """Implement the reaction to a message."""

        message = cast(HttpMessage, message)

        # recover dialogue
        http_dialogues = cast(HttpDialogues, self.context.http_dialogues)
        http_dialogue = cast(HttpDialogue, http_dialogues.update(message))
        if http_dialogue is None:
            self._handle_unidentified_dialogue(message)
            return

        if message.performative == HttpMessage.Performative.RESPONSE and message.status_code == 200:
            self._handle_response(message)
        elif message.performative == HttpMessage.Performative.REQUEST:
            self._handle_request(message, http_dialogue)
        else:
            self.context.logger.info(f"got unexpected http message: code = {message.status_code}")

    def _handle_response(self, http_msg: HttpMessage) -> None:
        """Handle an Http response."""

        model = self.context.advanced_data_request_model

        msg_body = json.loads(http_msg.body)

        success = False
        for output in model.outputs:
            json_path = output["json_path"]

            # find desired output data in msg_body
            value = cast(SupportsFloat, find(json_path, msg_body))

            # if value is a numeric type, store it as fixed-point with number of decimals
            if is_number(value):
                float_value = float(value)
                int_value = int(float_value * 10**model.decimals)
                observation = {output["name"]: {"value": int_value, "decimals": model.decimals}}
            elif isinstance(value, str):
                observation = {output["name"]: {"value": value}}
            else:
                self.context.logger.warning(f"No valid output for {output['name']} found in response.")
                continue
            success = True
            self.context.shared_state.update(observation)
            self.context.logger.info(f"Observation: {observation}")

        if success and self.context.prometheus_dialogues.enabled:
            metric_name = "num_retrievals"
            self.context.behaviours.advanced_data_request_behaviour.update_prometheus_metric(
                metric_name, "inc", 1.0, {}
            )

    def _handle_request(self, http_msg: HttpMessage, http_dialogue: HttpDialogue) -> None:
        """Handle a Http request."""
        self.context.logger.debug(
            f"received http request with method={http_msg.method}, url={http_msg.url} and body={http_msg.body!r}"
        )

        if http_msg.method == "get":
            self._handle_get(http_msg, http_dialogue)
        elif http_msg.method == "post":
            self.context.logger.info("method 'post' is not supported.")

    def _handle_get(self, http_msg: HttpMessage, http_dialogue: HttpDialogue) -> None:
        """Handle a Http request of verb GET."""
        model = self.context.data_request_model
        outputs = [output["name"] for output in model.outputs]
        data = {key: value for (key, value) in self.context.shared_state.items() if key in outputs}

        http_response = http_dialogue.reply(
            performative=HttpMessage.Performative.RESPONSE,
            target_message=http_msg,
            version=http_msg.version,
            status_code=200,
            status_text="Success",
            headers=http_msg.headers,
            body=json.dumps(data).encode("utf-8"),
        )
        self.context.logger.debug(f"responding with: {http_response}")
        self.context.outbox.put_message(message=http_response)

        if self.context.prometheus_dialogues.enabled:
            metric_name = "num_requests"
            self.context.behaviours.prometheus_behaviour.update_prometheus_metric(metric_name, "inc", 1.0, {})

    def _handle_unidentified_dialogue(self, msg: Message) -> None:
        """Handle an unidentified dialogue."""
        self.context.logger.info(f"received invalid message={msg}, unidentified dialogue.")

    def teardown(self) -> None:
        """Teardown the handler."""
