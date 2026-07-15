from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.message_thread_participant import (
    MessageThreadParticipant,
    ParticipantRole,
)
from app.services.base import CRUDService

from .message_thread import MessageThreadService
from .user import UserService


class ParticipantNotFoundError(Exception):
    pass


class MessageThreadParticipantService(CRUDService[MessageThreadParticipant]):
    model = MessageThreadParticipant
    not_found_error = ParticipantNotFoundError

    def add_participant(
        self,
        *,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
        role: ParticipantRole,
    ) -> MessageThreadParticipant:

        MessageThreadService(self.session).get_by_id_or_raise(thread_id)
        UserService(self.session).get_by_id(user_id)

        stmt = select(MessageThreadParticipant).where(
            MessageThreadParticipant.thread_id == thread_id,
            MessageThreadParticipant.user_id == user_id,
        )

        participant = self.session.scalar(stmt)

        if participant:
            return participant

        participant = MessageThreadParticipant(
            thread_id=thread_id,
            user_id=user_id,
            role=role,
        )

        self.session.add(participant)
        self.session.flush()

        return participant

    def remove_participant(
        self,
        *,
        thread_id: uuid.UUID,
        user_id: uuid.UUID,
    ):

        stmt = select(MessageThreadParticipant).where(
            MessageThreadParticipant.thread_id == thread_id,
            MessageThreadParticipant.user_id == user_id,
        )

        participant = self.session.scalar(stmt)

        if participant:
            self.session.delete(participant)

    def list_participants(
        self,
        thread_id: uuid.UUID,
    ):
        stmt = select(MessageThreadParticipant).where(
            MessageThreadParticipant.thread_id == thread_id,
        )

        return list(self.session.scalars(stmt))
