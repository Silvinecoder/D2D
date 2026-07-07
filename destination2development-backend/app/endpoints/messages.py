from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.message import (
    CreateMessageRequest,
    MessageResponse,
)
from app.services.message_service import MessageService

router = APIRouter(
    prefix="/message-threads/{thread_id}/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=MessageResponse,
)
def send_message(
    thread_id: uuid.UUID,
    request: CreateMessageRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = MessageService(session)

    message = service.send_message(
        thread_id=thread_id,
        sender=user,
        body=request.body,
    )

    session.commit()
    session.refresh(message)

    return message


@router.get(
    "",
    response_model=list[MessageResponse],
)
def list_messages(
    thread_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = MessageService(session)

    return service.list_messages(thread_id)


@router.patch(
    "/{message_id}/read",
    response_model=MessageResponse,
)
def mark_message_as_read(
    thread_id: uuid.UUID,
    message_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = MessageService(session)

    message = service.mark_as_read(message_id)

    session.commit()
    session.refresh(message)

    return message
