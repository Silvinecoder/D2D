from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationListResponse
from app.services.notification import (
    NotificationService,
    NotificationNotFoundError,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=NotificationListResponse,
)
def list_notifications(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    return service.list_notifications(user.id)


@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    try:
        notification = service.mark_as_read(
            notification_id=notification_id,
            user_id=user.id,
        )
    except NotificationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    session.commit()
    session.refresh(notification)

    return notification


@router.patch("/read-all")
def mark_all_notifications_as_read(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = NotificationService(session)

    updated = service.mark_all_as_read(user.id)

    session.commit()

    return {
        "success": True,
        "updated": updated,
    }
