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

"""This module contains the classes required for prometheus dialogue management.

- PrometheusDialogue: The dialogue class maintains state of a dialogue and manages it.
- PrometheusDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import cast
from collections.abc import Callable

from aea.common import Address
from aea.protocols.base import Message
from aea.protocols.dialogue.base import Dialogue, Dialogues, DialogueLabel

from packages.eightballer.protocols.prometheus.message import PrometheusMessage


class PrometheusDialogue(Dialogue):
    """The prometheus dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset(
        {
            PrometheusMessage.Performative.ADD_METRIC,
            PrometheusMessage.Performative.UPDATE_METRIC,
        }
    )
    TERMINAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset({PrometheusMessage.Performative.RESPONSE})
    VALID_REPLIES: dict[Message.Performative, frozenset[Message.Performative]] = {
        PrometheusMessage.Performative.ADD_METRIC: frozenset({PrometheusMessage.Performative.RESPONSE}),
        PrometheusMessage.Performative.RESPONSE: frozenset(),
        PrometheusMessage.Performative.UPDATE_METRIC: frozenset({PrometheusMessage.Performative.RESPONSE}),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a prometheus dialogue."""

        AGENT = "agent"
        SERVER = "server"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a prometheus dialogue."""

        SUCCESSFUL = 0

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: Dialogue.Role,
        message_class: type[PrometheusMessage] = PrometheusMessage,
    ) -> None:
        """Initialize a dialogue."""
        Dialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            message_class=message_class,
            self_address=self_address,
            role=role,
        )


class PrometheusDialogues(Dialogues, ABC):
    """This class keeps track of all prometheus dialogues."""

    END_STATES = frozenset({PrometheusDialogue.EndState.SUCCESSFUL})

    _keep_terminal_state_dialogues = False

    def __init__(
        self,
        self_address: Address,
        role_from_first_message: Callable[[Message, Address], Dialogue.Role],
        dialogue_class: type[PrometheusDialogue] = PrometheusDialogue,
    ) -> None:
        """Initialize dialogues."""
        Dialogues.__init__(
            self,
            self_address=self_address,
            end_states=cast(frozenset[Dialogue.EndState], self.END_STATES),
            message_class=PrometheusMessage,
            dialogue_class=dialogue_class,
            role_from_first_message=role_from_first_message,
        )
