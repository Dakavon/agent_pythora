# ------------------------------------------------------------------------------
#
#   Copyright 2018-2023 Fetch.AI Limited
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

"""This package contains dialogues used by the advanced_data_request skill."""

from typing import Any

from aea.skills.base import Model
from aea.protocols.base import Address, Message
from aea.protocols.dialogue.base import Dialogue as BaseDialogue

from packages.eightballer.protocols.http.dialogues import (
    HttpDialogue as BaseHttpDialogue,
    HttpDialogues as BaseHttpDialogues,
)
from packages.eightballer.protocols.prometheus.dialogues import (
    PrometheusDialogue as BasePrometheusDialogue,
    PrometheusDialogues as BasePrometheusDialogues,
)


HttpDialogue = BaseHttpDialogue
PrometheusDialogue = BasePrometheusDialogue
HttpDialogues = BaseHttpDialogues


class PrometheusDialogues(Model, BasePrometheusDialogues):
    """The dialogues class keeps track of all prometheus dialogues."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize dialogues."""
        self.enabled = kwargs.pop("enabled", False)
        self.metrics = kwargs.pop("metrics", [])

        Model.__init__(self, **kwargs)

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message."""
            del receiver_address, message
            return PrometheusDialogue.Role.AGENT

        BasePrometheusDialogues.__init__(
            self,
            self_address=str(self.skill_id),
            role_from_first_message=role_from_first_message,
        )
