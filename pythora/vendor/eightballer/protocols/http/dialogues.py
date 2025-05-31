"""This module contains the classes required for http dialogue management.

- HttpDialogue: The dialogue class maintains state of a dialogue and manages it.
- HttpDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import cast
from collections.abc import Callable

from aea.common import Address
from aea.skills.base import Model
from aea.protocols.base import Message
from aea.protocols.dialogue.base import Dialogue, Dialogues, DialogueLabel

from packages.eightballer.protocols.http.message import HttpMessage


def _role_from_first_message(message: Message, sender: Address) -> Dialogue.Role:
    """Infer the role of the agent from an incoming/outgoing first message."""
    del sender, message
    return HttpDialogue.Role.CLIENT


class HttpDialogue(Dialogue):
    """The http dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset({HttpMessage.Performative.REQUEST})
    TERMINAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset({HttpMessage.Performative.RESPONSE})
    VALID_REPLIES: dict[Message.Performative, frozenset[Message.Performative]] = {
        HttpMessage.Performative.REQUEST: frozenset({HttpMessage.Performative.RESPONSE}),
        HttpMessage.Performative.RESPONSE: frozenset(),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a http dialogue."""

        CLIENT = "client"
        SERVER = "server"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a http dialogue."""

        SUCCESSFUL = 0

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: Dialogue.Role,
        message_class: type[HttpMessage] = HttpMessage,
    ) -> None:
        """Initialize a dialogue.



        Args:
        ----
               dialogue_label:  the identifier of the dialogue
               self_address:  the address of the entity for whom this dialogue is maintained
               role:  the role of the agent this dialogue is maintained for
               message_class:  the message class used

        """
        Dialogue.__init__(
            self, dialogue_label=dialogue_label, message_class=message_class, self_address=self_address, role=role
        )


class BaseHttpDialogues(Dialogues, ABC):
    """This class keeps track of all http dialogues."""

    END_STATES = frozenset({HttpDialogue.EndState.SUCCESSFUL})
    _keep_terminal_state_dialogues = False

    def __init__(
        self,
        self_address: Address,
        role_from_first_message: Callable[[Message, Address], Dialogue.Role] = _role_from_first_message,
        dialogue_class: type[HttpDialogue] = HttpDialogue,
    ) -> None:
        """Initialize dialogues.



        Args:
        ----
               self_address:  the address of the entity for whom dialogues are maintained
               dialogue_class:  the dialogue class used
               role_from_first_message:  the callable determining role from first message

        """
        Dialogues.__init__(
            self,
            self_address=self_address,
            end_states=cast(frozenset[Dialogue.EndState], self.END_STATES),
            message_class=HttpMessage,
            dialogue_class=dialogue_class,
            role_from_first_message=role_from_first_message,
        )


class HttpDialogues(BaseHttpDialogues, Model):
    """This class defines the dialogues used in Http."""

    def __init__(self, **kwargs):
        """Initialize dialogues."""
        Model.__init__(self, keep_terminal_state_dialogues=False, **kwargs)
        BaseHttpDialogues.__init__(
            self, self_address=str(self.context.skill_id), role_from_first_message=_role_from_first_message
        )
