from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def list_notifications(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    return service.list_notifications(user.id)


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    notification = service.mark_as_read(notification_id)

    session.commit()
    session.refresh(notification)

    return notification


@router.patch(
    "/read-all",
)
def mark_all_notifications_as_read(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    service.mark_all_as_read(user.id)

    session.commit()

    return {
        "success": True,
    }
