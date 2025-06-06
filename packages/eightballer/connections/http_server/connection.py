# ------------------------------------------------------------------------------
#
#   Copyright 2023 8baller
#   Copyright 2022 Valory AG
#   Copyright 2018-2021 Fetch.AI Limited
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
"""HTTP server connection, channel, server, and handler."""

import ssl
import email
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, cast
from asyncio import CancelledError
from textwrap import dedent
from traceback import format_exc
from urllib.parse import parse_qs, urlparse
from asyncio.events import AbstractEventLoop
from asyncio.futures import Future
from concurrent.futures._base import CancelledError as FuturesCancelledError  # noqa

from aiohttp import web
from aea.common import Address
from openapi_core import create_spec
from aea.mail.base import Message, Envelope
from aiohttp.web_request import BaseRequest
from aea.connections.base import Connection, ConnectionStates
from aea.configurations.base import PublicId
from werkzeug.datastructures import (
    ImmutableMultiDict,
)  # pylint: disable=wrong-import-order
from aea.protocols.dialogue.base import Dialogue as BaseDialogue, DialogueLabel
from openapi_spec_validator.schemas import (
    read_yaml_file,
)  # pylint: disable=wrong-import-order
from openapi_spec_validator.exceptions import (
    OpenAPIValidationError,
)  # pylint: disable=wrong-import-order
from openapi_core.validation.request.datatypes import (
    Headers,
    OpenAPIRequest,
    RequestParameters,
)
from openapi_core.validation.request.shortcuts import validate_request
from openapi_core.validation.request.validators import RequestValidator

from packages.eightballer.protocols.http.message import HttpMessage
from packages.eightballer.protocols.http.dialogues import (
    HttpDialogue,
    BaseHttpDialogues,
)


SUCCESS = 200
NOT_FOUND = 404
REQUEST_TIMEOUT = 408
SERVER_ERROR = 500

_default_logger = logging.getLogger("aea.packages.eightballer.connections.http_server")

RequestId = DialogueLabel
PUBLIC_ID = PublicId.from_str("eightballer/http_server:0.1.0")


class HttpDialogues(BaseHttpDialogues):
    """The dialogues class keeps track of all http dialogues."""

    def __init__(self, self_address: Address, **kwargs: Any) -> None:
        """Initialize dialogues."""

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message."""
            del receiver_address, message
            return HttpDialogue.Role.CLIENT

        BaseHttpDialogues.__init__(
            self,
            self_address=self_address,
            role_from_first_message=role_from_first_message,
            **kwargs,
        )


def headers_to_string(headers: dict) -> str:
    """Convert headers to string."""
    msg = email.message.Message()
    for name, value in headers.items():
        msg.add_header(name, value)
    return msg.as_string()


class Request(OpenAPIRequest):
    """Generic request object."""

    @property
    def is_id_set(self) -> bool:
        """Check if id is set."""
        return self._id is not None

    @property
    def id(self) -> RequestId:  # pylint: disable=C0103
        """Get the request id."""
        return self._id

    @id.setter
    def id(self, request_id: RequestId) -> None:  # pylint: disable=C0103
        """Set the request id."""
        self._id = request_id

    @classmethod
    async def create(cls, http_request: BaseRequest, extra_headers: dict[str, str] | None = None) -> "Request":
        """Create a request."""
        method = http_request.method.lower()

        parsed_path = urlparse(http_request.path_qs)

        url = http_request.url

        body = await http_request.read()

        mimetype = http_request.content_type

        query_params = parse_qs(parsed_path.query, keep_blank_values=True)

        parameters = RequestParameters(
            query=ImmutableMultiDict(query_params),
            header=Headers([]),
            cookie={},
        )

        request = Request(
            full_url_pattern=str(url),
            method=method,
            parameters=parameters,
            body=body,
            mimetype=mimetype,
        )
        all_headers = dict(http_request.headers)
        if extra_headers:
            all_headers.update(extra_headers)
            del all_headers["Sec-Fetch-Mode"]
            del all_headers["Sec-Fetch-Site"]
        request.parameters.header = headers_to_string(all_headers)
        return request

    def to_envelope_and_set_id(
        self,
        dialogues: HttpDialogues,
        target_skill_id: PublicId,
    ) -> Envelope:
        """Process incoming API request by packaging into Envelope and sending it in-queue."""
        url = self.full_url_pattern
        http_message, http_dialogue = dialogues.create(
            counterparty=str(target_skill_id),
            performative=HttpMessage.Performative.REQUEST,
            method=self.method,
            url=url,
            headers=self.parameters.header,
            body=self.body if self.body is not None else b"",
            version="",
        )
        dialogue = cast(HttpDialogue, http_dialogue)
        self.id = dialogue.incomplete_dialogue_label  # pylint: disable=C0103
        return Envelope(
            to=http_message.to,
            sender=http_message.sender,
            message=http_message,
        )


class Response(web.Response):
    """Generic response object."""

    @classmethod
    def from_message(cls, http_message: HttpMessage) -> "Response":
        """Turn an envelope into a response."""
        if http_message.performative == HttpMessage.Performative.RESPONSE:
            if http_message.is_set("headers") and http_message.headers:
                headers: dict | None = dict(email.message_from_string(http_message.headers).items())
            else:
                headers = None

            # if content length header provided, it should correspond to actuyal body length
            if headers and "Content-Length" in headers:
                headers["Content-Length"] = str(len(http_message.body or ""))

            response = cls(
                status=http_message.status_code,
                reason=http_message.status_text,
                body=http_message.body,
                headers=headers,
            )
        else:  # pragma: nocover
            response = cls(status=SERVER_ERROR, text="Server error")
        return response


class APISpec:
    """API Spec class to verify a request against an OpenAPI/Swagger spec."""

    def __init__(
        self,
        api_spec_path: str | None = None,
        server: str | None = None,
        logger: logging.Logger = _default_logger,
    ):
        """Initialize the API spec."""
        self._validator = None  # type: Optional[RequestValidator]
        self.logger = logger
        if api_spec_path is not None:
            try:
                api_spec_dict = read_yaml_file(api_spec_path)
                if server is not None:
                    api_spec_dict["servers"].append({"url": server})
                api_spec = create_spec(api_spec_dict)
                self._validator = RequestValidator(api_spec)
            except OpenAPIValidationError as error:
                self.logger.exception(f"API specification YAML source file not correctly formatted: {error!s}")
            except Exception:
                self.logger.exception("API specification YAML source file not correctly formatted.")
                raise

    def verify(self, request: Request) -> bool:
        """Verify a http_method, url and param against the provided API spec."""
        if self._validator is None:
            self.logger.debug("Skipping API verification!")
            return True

        try:
            validate_request(self._validator, request)
        except Exception:  # pragma: nocover # pylint: disable=broad-except
            self.logger.exception("APISpec verify error")
            return False
        return True


class BaseAsyncChannel(ABC):
    """Base asynchronous channel class."""

    def __init__(self, address: Address, connection_id: PublicId) -> None:
        """Initialize a channel."""
        self._in_queue = None  # type: Optional[asyncio.Queue]
        self._loop = None  # type: Optional[asyncio.AbstractEventLoop]
        self.is_stopped = True
        self.address = address
        self.connection_id = connection_id

    @abstractmethod
    async def connect(self, loop: AbstractEventLoop) -> None:
        """Connect.

        Upon HTTP Channel connection, start the HTTP Server in its own thread.

        """
        self._loop = loop
        self._in_queue = asyncio.Queue()
        self.is_stopped = False

    async def get_message(self) -> Optional["Envelope"]:
        """Get http response from in-queue."""
        if self._in_queue is None:
            msg = "Looks like channel is not connected!"
            raise ValueError(msg)

        try:
            return await self._in_queue.get()
        except CancelledError:  # pragma: nocover
            return None

    @abstractmethod
    def send(self, envelope: Envelope) -> None:
        """Send the envelope in_queue."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect.

        Shut-off the HTTP Server.
        """


class HTTPChannel(BaseAsyncChannel):  # pylint: disable=too-many-instance-attributes
    """A wrapper for an RESTful API with an internal HTTPServer."""

    RESPONSE_TIMEOUT = 150.0

    def __init__(
        self,
        address: Address,
        host: str,
        port: int,
        target_skill_id: PublicId,
        api_spec_path: str | None,
        connection_id: PublicId,
        timeout_window: float = RESPONSE_TIMEOUT,
        logger: logging.Logger = _default_logger,
        ssl_cert_path: str | None = None,
        ssl_key_path: str | None = None,
    ):
        """Initialize a channel and process the initial API specification from the file path (if given)."""
        super().__init__(address=address, connection_id=connection_id)
        self.host = host
        self.port = port
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        self.target_skill_id = target_skill_id
        if self.ssl_cert_path and self.ssl_key_path:
            self.server_address = f"https://{self.host}:{self.port}"
        else:
            self.server_address = f"http://{self.host}:{self.port}"

        self._api_spec = APISpec(api_spec_path, self.server_address, logger)
        self.timeout_window = timeout_window
        self.http_server: web.TCPSite | None = None
        self.pending_requests: dict[RequestId, Future] = {}
        self._dialogues = HttpDialogues(str(HTTPServerConnection.connection_id))
        self.logger = logger

    @property
    def api_spec(self) -> APISpec:
        """Get the api spec."""
        return self._api_spec

    async def connect(self, loop: AbstractEventLoop) -> None:
        """Connect.

        Upon HTTP Channel connection, start the HTTP Server in its own thread.

        """
        if self.is_stopped:
            await super().connect(loop)

            try:
                await self._start_http_server()
                self.logger.info(f"HTTP Server has connected to port: {self.port}.")
            except Exception:  # pragma: nocover # pylint: disable=broad-except
                self.is_stopped = True
                self._in_queue = None
                self.logger.exception(f"Failed to start server on {self.host}:{self.port}.")

    async def _http_handler(self, http_request: BaseRequest) -> Response:
        """Verify the request then send the request to Agent as an envelope."""
        request = await Request.create(http_request)
        if self._in_queue is None:  # pragma: nocover
            msg = "Channel not connected!"
            raise ValueError(msg)

        is_valid_request = self.api_spec.verify(request)

        if not is_valid_request:
            self.logger.warning(f"request is not valid: {request}")
            return Response(status=NOT_FOUND, reason="Request Not Found")

        try:
            # turn request into envelope
            envelope = request.to_envelope_and_set_id(self._dialogues, self.target_skill_id)

            self.pending_requests[request.id] = Future()

            # send the envelope to the agent's inbox (via self.in_queue)
            await self._in_queue.put(envelope)
            # wait for response envelope within given timeout window (self.timeout_window)
            # to appear in dispatch_ready_envelopes

            response_message = await asyncio.wait_for(
                self.pending_requests[request.id],
                timeout=self.timeout_window,
            )
            return Response.from_message(response_message)

        except TimeoutError:
            self.logger.warning(
                dedent(f"""
                        Request timed out! Request={request} not handled as a result. "
                        Ensure requests (protocol_id={HttpMessage.protocol_id}) are handled by a skill!"
                        """)
            )
            return Response(status=REQUEST_TIMEOUT, reason="Request Timeout")
        except FuturesCancelledError:
            return Response(status=SERVER_ERROR, reason="Server terminated unexpectedly.")  # pragma: nocover
        except BaseException:  # pragma: nocover # pylint: disable=broad-except
            self.logger.exception("Error during handling incoming request")
            return Response(status=SERVER_ERROR, reason="Server Error", text=format_exc())
        finally:
            if request.is_id_set:
                self.pending_requests.pop(request.id, None)

    async def _start_http_server(self) -> None:
        """Start http server."""
        server = web.Server(self._http_handler)
        runner = web.ServerRunner(server)
        await runner.setup()
        ssl_context = None
        if self.ssl_cert_path and self.ssl_key_path:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(self.ssl_cert_path, self.ssl_key_path)
        self.http_server = web.TCPSite(runner, self.host, self.port, ssl_context=ssl_context)
        await self.http_server.start()

    def send(self, envelope: Envelope) -> None:
        """Send the envelope in_queue."""
        if self.http_server is None:  # pragma: nocover
            msg = "Server not connected, call connect first!"
            raise ValueError(msg)

        message = cast(HttpMessage, envelope.message)
        dialogue = self._dialogues.update(message)

        if dialogue is None:
            self.logger.warning(f"Could not create dialogue for message={message}")
            return

        future = self.pending_requests.pop(dialogue.incomplete_dialogue_label, None)

        if not future:
            self.logger.warning(
                dedent(f"""
                       Dropping message={message} for "
                       incomplete_dialogue_label={dialogue.incomplete_dialogue_label} which has timed out."
                        """)
            )
            return
        if not future.done():
            future.set_result(message)

    async def disconnect(self) -> None:
        """Disconnect.

        Shut-off the HTTP Server.
        """
        if self.http_server is None:  # pragma: nocover
            msg = "Server not connected, call connect first!"
            raise ValueError(msg)

        if not self.is_stopped:
            await self.http_server.stop()
            self.logger.info(f"HTTP Server has shutdown on port: {self.port}.")
            self.is_stopped = True
            self._in_queue = None


class HTTPServerConnection(Connection):
    """Proxy to the functionality of the http server implementing a RESTful API specification."""

    connection_id = PUBLIC_ID

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a HTTP server connection."""
        super().__init__(**kwargs)
        host = cast(str | None, self.configuration.config.get("host"))
        port = cast(int | None, self.configuration.config.get("port"))
        target_skill_id_ = cast(str | None, self.configuration.config.get("target_skill_id"))
        if host is None or port is None or target_skill_id_ is None:  # pragma: nocover
            msg = "host and port and target_skill_id must be set!"
            raise ValueError(msg)
        target_skill_id = PublicId.try_from_str(target_skill_id_)
        if target_skill_id is None:  # pragma: nocover
            msg = "Provided target_skill_id is not a valid public id."
            raise ValueError(msg)
        api_spec_path = cast(str | None, self.configuration.config.get("api_spec_path"))
        ssl_cert_path = cast(str | None, self.configuration.config.get("ssl_cert"))
        ssl_key_path = cast(str | None, self.configuration.config.get("ssl_key"))

        if bool(ssl_cert_path) != bool(ssl_key_path):  # pragma: nocover
            msg = "Please specify both ssl_cert and ssl_key or neither."
            raise ValueError(msg)

        self.channel = HTTPChannel(
            self.address,
            host,
            port,
            target_skill_id,
            api_spec_path,
            connection_id=self.connection_id,
            logger=self.logger,
            ssl_cert_path=ssl_cert_path,
            ssl_key_path=ssl_key_path,
        )

    async def connect(self) -> None:
        """Connect to the http channel."""
        if self.is_connected:
            return

        self.state = ConnectionStates.connecting
        self.channel.logger = self.logger
        await self.channel.connect(loop=self.loop)
        if self.channel.is_stopped:
            self.state = ConnectionStates.disconnected
        else:
            self.state = ConnectionStates.connected

    async def disconnect(self) -> None:
        """Disconnect from HTTP channel."""
        if self.is_disconnected:
            return

        self.state = ConnectionStates.disconnecting
        await self.channel.disconnect()
        self.state = ConnectionStates.disconnected

    async def send(self, envelope: "Envelope") -> None:
        """Send an envelope."""
        self._ensure_connected()
        self.channel.send(envelope)

    async def receive(self, *args: Any, **kwargs: Any) -> Optional["Envelope"]:
        """Receive an envelope."""
        del args, kwargs
        self._ensure_connected()
        try:
            return await self.channel.get_message()
        except CancelledError:  # pragma: no cover
            return None
