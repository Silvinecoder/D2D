from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.message_thread import (
    CreateMessageThreadRequest,
    MessageThreadResponse,
)
from app.services.message_thread_service import MessageThreadService

router = APIRouter(
    prefix="/message-threads",
    tags=["Message Threads"],
)


@router.post(
    "",
    response_model=MessageThreadResponse,
)
def create_message_thread(
    request: CreateMessageThreadRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = MessageThreadService(session)

    thread = service.create_thread(
        creator=user,
        message_type=request.message_type,
        subject=request.subject,
    )

    session.commit()
    session.refresh(thread)

    return thread


@router.get(
    "",
    response_model=list[MessageThreadResponse],
)
def list_message_threads(
    session: Session = Depends(get_db),
):
    service = MessageThreadService(session)

    return service.list_threads()


@router.get(
    "/{thread_id}",
    response_model=MessageThreadResponse,
)
def get_message_thread(
    thread_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = MessageThreadService(session)

    return service.get_by_id_or_raise(thread_id)
