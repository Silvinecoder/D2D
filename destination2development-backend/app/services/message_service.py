from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.message import Message
from app.models.user import User
from app.services.base_service import CRUDService, utcnow

from .message_thread_service import MessageThreadService


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

        MessageThreadService(self.session).get_by_id_or_raise(thread_id)

        message = Message(
            thread_id=thread_id,
            sender_id=sender.id,
            body=body,
        )

        self.session.add(message)
        self.session.flush()

        MessageThreadService(self.session).update_last_message(thread_id)

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

    def mark_as_read(self, message_id: uuid.UUID):
        message = self.get_by_id_or_raise(message_id)
        message.read_at = utcnow()
        return message
