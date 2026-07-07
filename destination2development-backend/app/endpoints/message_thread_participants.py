from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.message_thread_participant import (
    AddMessageThreadParticipantRequest,
    MessageThreadParticipantResponse,
    RemoveMessageThreadParticipantRequest,
)
from app.services.message_thread_participant_service import (
    MessageThreadParticipantService,
)

router = APIRouter(
    prefix="/message-thread-participants",
    tags=["Message Thread Participants"],
)


@router.post(
    "",
    response_model=MessageThreadParticipantResponse,
)
def add_message_thread_participant(
    request: AddMessageThreadParticipantRequest,
    session: Session = Depends(get_db),
):
    service = MessageThreadParticipantService(session)

    participant = service.add_participant(
        thread_id=request.thread_id,
        user_id=request.user_id,
        role=request.role,
    )

    session.commit()
    session.refresh(participant)

    return participant


@router.get(
    "/{thread_id}",
    response_model=list[MessageThreadParticipantResponse],
)
def list_message_thread_participants(
    thread_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = MessageThreadParticipantService(session)

    return service.list_participants(thread_id)


@router.delete(
    "",
    status_code=204,
)
def remove_message_thread_participant(
    request: RemoveMessageThreadParticipantRequest,
    session: Session = Depends(get_db),
):
    service = MessageThreadParticipantService(session)

    service.remove_participant(
        thread_id=request.thread_id,
        user_id=request.user_id,
    )

    session.commit()
