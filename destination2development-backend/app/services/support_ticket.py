from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.events import publish
from app.models.message_thread import MessageThreadType
from app.models.support_ticket import (
    SupportTicket,
    TicketStatus,
    can_transition,
)
from app.models.user import User, SystemRole
from app.services.base import CRUDService, utcnow

from .message_thread_participant import MessageThreadParticipantService
from .message_thread import MessageThreadService


class SupportTicketNotFoundError(Exception):
    pass


class InvalidAssigneeError(Exception):
    pass


class TicketAlreadyAssignedError(Exception):
    pass


class InvalidTicketTransitionError(Exception):
    def __init__(self, current: TicketStatus, target: TicketStatus):
        self.current = current
        self.target = target
        super().__init__(f"Cannot move ticket from {current} to {target}")


class SupportTicketService(CRUDService[SupportTicket]):
    model = SupportTicket
    not_found_error = SupportTicketNotFoundError

    def create_ticket(
        self,
        *,
        creator: User,
        subject: str,
    ) -> SupportTicket:

        thread = MessageThreadService(self.session).create_thread(
            creator=creator,
            message_type=MessageThreadType.ticket,
            subject=subject,
        )

        ticket = SupportTicket(
            thread_id=thread.id,
            status=TicketStatus.open,
        )

        self.session.add(ticket)
        self.session.flush()

        return ticket

    def get_by_thread_id_or_raise(
        self,
        thread_id: uuid.UUID,
    ) -> SupportTicket:
        stmt = select(SupportTicket).where(
            SupportTicket.thread_id == thread_id,
        )

        ticket = self.session.scalar(stmt)

        if ticket is None:
            raise self.not_found_error

        return ticket

    def list_tickets(
        self,
        *,
        status: TicketStatus | None = None,
        assigned_admin_id: uuid.UUID | None = None,
        unassigned: bool = False,
    ):
        stmt = select(SupportTicket)

        if status is not None:
            stmt = stmt.where(
                SupportTicket.status == status,
            )

        if assigned_admin_id is not None:
            stmt = stmt.where(
                SupportTicket.assigned_admin_id == assigned_admin_id,
            )

        if unassigned:
            stmt = stmt.where(
                SupportTicket.assigned_admin_id.is_(None),
            )

        return list(self.session.scalars(stmt))

    def update_status(
        self,
        ticket_id: uuid.UUID,
        status: TicketStatus,
    ) -> SupportTicket:
        ticket = self.get_by_id_or_raise(ticket_id)

        if not can_transition(ticket.status, status):
            raise InvalidTicketTransitionError(
                ticket.status,
                status,
            )

        ticket.status = status

        if status == TicketStatus.resolved:
            ticket.resolved_at = utcnow()
        elif status == TicketStatus.closed:
            ticket.closed_at = utcnow()

        thread = MessageThreadService(self.session).get_by_id_or_raise(ticket.thread_id)

        publish(
            "ticket.status_changed",
            session=self.session,
            ticket_id=ticket.id,
            thread_created_by=thread.created_by,
            new_status=status.value,
        )

        return ticket

    def assign_ticket(
        self,
        *,
        ticket_id: uuid.UUID,
        admin: User,
    ) -> SupportTicket:
        ticket = self.get_by_id_or_raise(ticket_id)

        if admin.system_role != SystemRole.admin:
            raise InvalidAssigneeError(
                "Support tickets may only be assigned to admins."
            )

        ticket.assigned_admin_id = admin.id

        if ticket.status == TicketStatus.open:
            ticket.status = TicketStatus.in_progress

        return ticket

    def claim_ticket(
        self,
        *,
        ticket_id: uuid.UUID,
        admin: User,
    ) -> SupportTicket:
        ticket = self.get_by_id_or_raise(ticket_id)

        if admin.system_role != SystemRole.admin:
            raise InvalidAssigneeError()

        if ticket.assigned_admin_id is not None:
            raise TicketAlreadyAssignedError()

        ticket.assigned_admin_id = admin.id

        MessageThreadParticipantService(self.session).add_participant(
            thread_id=ticket.thread_id,
            user_id=admin.id,
        )

        if ticket.status == TicketStatus.open:
            ticket.status = TicketStatus.in_progress

        return ticket

    def unassign_ticket(
        self,
        *,
        ticket_id: uuid.UUID,
    ) -> SupportTicket:
        ticket = self.get_by_id_or_raise(ticket_id)

        ticket.assigned_admin_id = None

        if ticket.status == TicketStatus.in_progress:
            ticket.status = TicketStatus.open

        return ticket
