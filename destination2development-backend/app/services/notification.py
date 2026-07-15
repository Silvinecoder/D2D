from __future__ import annotations

import uuid

from sqlalchemy import func, select, update

from app.models.notification import (
    Notification,
    NotificationEntityType,
    NotificationEventType,
)
from app.services.base import CRUDService, utcnow


class NotificationNotFoundError(Exception):
    pass


class NotificationService(CRUDService[Notification]):
    """Notification service."""

    model = Notification
    not_found_error = NotificationNotFoundError

    def create_notification(
        self,
        *,
        user_id: uuid.UUID,
        event_type: NotificationEventType,
        entity_type: NotificationEntityType,
        entity_id: uuid.UUID,
        title: str,
        body: str,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            body=body,
        )

        self.session.add(notification)
        self.session.flush()

        return notification

    def list_notifications(self, user_id: uuid.UUID):
        notifications = list(
            self.session.scalars(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(
                    Notification.read_at.is_not(None),
                    Notification.created_at.desc(),
                )
            )
        )

        unread_count = (
            self.session.scalar(
                select(func.count(Notification.id)).where(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                )
            )
            or 0
        )

        return {
            "items": notifications,
            "unread_count": unread_count,
        }

    def mark_as_read(
        self,
        *,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Notification:
        notification = self.session.scalar(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )

        if notification is None:
            raise NotificationNotFoundError()

        if notification.read_at is None:
            notification.read_at = utcnow()

        return notification

    def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        result = self.session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .values(read_at=utcnow())
        )

        return result.rowcount or 0
