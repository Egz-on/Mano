import pytest

from mano.domain.exceptions.chat_exceptions import MessageValidationError
from mano.domain.models.conversation import ConversationId
from mano.domain.models.message import Message
from mano.domain.models.user import UserId


def test_message_create_trims_content() -> None:
    message = Message.create(
        conversation_id=ConversationId("11111111-1111-1111-1111-111111111111"),
        sender_id=UserId("22222222-2222-2222-2222-222222222222"),
        content="  hello  ",
    )

    assert message.content == "hello"


def test_message_rejects_blank_content() -> None:
    with pytest.raises(MessageValidationError):
        Message.create(
            conversation_id=ConversationId("11111111-1111-1111-1111-111111111111"),
            sender_id=UserId("22222222-2222-2222-2222-222222222222"),
            content="   ",
        )
