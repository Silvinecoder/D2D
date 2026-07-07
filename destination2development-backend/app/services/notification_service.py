from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.notification import Notification
from app.models.user import User
from app.services.base_service import CRUDService, utcnow


class NotificationNotFoundError(Exception):
    pass


class NotificationService(CRUDService[Notification]):
    model = Notification
    not_found_error = NotificationNotFoundError

    def create_notification(
        self,
        *,
        user: User,
        event_type: str,
        entity_type: str,
        entity_id: uuid.UUID,
        title: str,
        body: str,
    ) -> Notification:

        notification = Notification(
            user_id=user.id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            title=title,
            body=body,
        )

        self.session.add(notification)
        self.session.flush()

        return notification

    def list_notifications(
        self,
        user_id: uuid.UUID,
    ) -> list[Notification]:

        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )

        return list(self.session.scalars(stmt))

    def mark_as_read(
        self,
        notification_id: uuid.UUID,
    ) -> Notification:

        notification = self.get_by_id_or_raise(notification_id)
        notification.read_at = utcnow()

        return notification

    def mark_all_as_read(
        self,
        user_id: uuid.UUID,
    ):

        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )

        for notification in self.session.scalars(stmt):
            notification.read_at = utcnow()
