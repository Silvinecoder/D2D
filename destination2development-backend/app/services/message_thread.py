from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.message_thread import MessageThread, MessageThreadType
from app.models.message_thread_participant import MessageThreadParticipant
from app.models.user import User
from app.services.base import CRUDService, utcnow


class MessageThreadNotFoundError(Exception):
    pass


class MessageThreadService(CRUDService[MessageThread]):
    model = MessageThread
    not_found_error = MessageThreadNotFoundError

    def create_thread(
        self,
        *,
        creator: User,
        message_type: MessageThreadType,
        subject: str | None = None,
    ) -> MessageThread:

        thread = MessageThread(
            message_type=message_type,
            subject=subject,
            created_by=creator.id,
        )

        self.session.add(thread)
        self.session.flush()

        # The creator is automatically the first participant.
        participant = MessageThreadParticipant(
            thread_id=thread.id,
            user_id=creator.id,
        )

        self.session.add(participant)
        self.session.flush()

        return thread

    def list_threads(self):
        stmt = select(MessageThread).order_by(
            MessageThread.last_message_at.desc(),
        )

        return list(self.session.scalars(stmt))

    def update_last_message(
        self,
        thread_id: uuid.UUID,
    ):
        thread = self.get_by_id_or_raise(thread_id)
        thread.last_message_at = utcnow()

        return thread
