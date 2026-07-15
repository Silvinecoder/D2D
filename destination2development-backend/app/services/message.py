from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.events import publish
from app.models.message import Message
from app.models.user import User
from app.services.base import CRUDService, utcnow

from .message_thread import MessageThreadService
from .message_thread_participant import MessageThreadParticipantService


class MessageNotFoundError(Exception):
    pass


class MessageService(CRUDService[Message]):
    model = Message
    not_found_error = MessageNotFoundError

    def send_message(
        self,
        *,
        thread_id: uuid.UUID,
        sender: User,
        body: str,
    ) -> Message:

        thread = MessageThreadService(self.session).get_by_id_or_raise(thread_id)

        message = Message(
            thread_id=thread_id,
            sender_id=sender.id,
            body=body,
        )

        self.session.add(message)
        self.session.flush()

        MessageThreadService(self.session).update_last_message(thread_id)

        participants = MessageThreadParticipantService(self.session).list_participants(
            thread_id
        )

        publish(
            "message.sent",
            session=self.session,
            thread_id=thread_id,
            sender=sender,
            thread_subject=thread.subject,
            participants=participants,
        )

        return message

    def list_messages(
        self,
        thread_id: uuid.UUID,
    ):
        stmt = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at)
        )

        return list(self.session.scalars(stmt))
