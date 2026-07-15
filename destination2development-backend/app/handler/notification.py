from __future__ import annotations

import uuid

from app.core.events import subscribe
from app.models.message_thread_participant import MessageThreadParticipant
from app.models.user import User
from app.services.notification import NotificationService
from app.models.notification import (
    NotificationEntityType,
    NotificationEventType,
)


@subscribe("message.sent")
def notify_on_message_sent(
    *,
    session,
    thread_id: uuid.UUID,
    sender: User,
    thread_subject: str | None,
    participants: list[MessageThreadParticipant],
) -> None:
    notification_service = NotificationService(session)

    for participant in participants:
        if participant.user_id == sender.id:
            continue

        notification_service.create_notification(
            user_id=participant.user_id,
            event_type=NotificationEventType.message_sent,
            entity_type=NotificationEntityType.thread,
            entity_id=thread_id,
            title=thread_subject or "New message",
            body=f"{sender.name} sent a new message.",
        )


@subscribe("ticket.status_changed")
def notify_on_ticket_status_changed(
    *,
    session,
    ticket_id: uuid.UUID,
    thread_created_by: uuid.UUID,
    new_status: str,
) -> None:
    if new_status not in ("resolved", "closed"):
        return

    NotificationService(session).create_notification(
        user_id=thread_created_by,
        event_type=NotificationEventType.ticket_created,
        entity_type=NotificationEntityType.ticket,
        entity_id=ticket_id,
        title="Your support ticket was updated",
        body=f"Your ticket is now {new_status}.",
    )
