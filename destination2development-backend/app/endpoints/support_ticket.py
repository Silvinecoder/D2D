from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_role
from app.models.support_ticket import TicketStatus
from app.models.user import SystemRole, User
from app.schemas.support_ticket import (
    AssignTicketRequest,
    CreateSupportTicketRequest,
    SupportTicketResponse,
    UpdateTicketStatusRequest,
)
from app.services.support_ticket import (
    InvalidAssigneeError,
    InvalidTicketTransitionError,
    SupportTicketService,
    TicketAlreadyAssignedError,
)
from app.services.user import UserService

router = APIRouter(
    prefix="/support-tickets",
    tags=["Support Tickets"],
)


@router.post(
    "",
    response_model=SupportTicketResponse,
)
def create_support_ticket(
    request: CreateSupportTicketRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    ticket = service.create_ticket(
        creator=user,
        subject=request.subject,
    )

    session.commit()
    session.refresh(ticket)

    return ticket


@router.get(
    "",
    response_model=list[SupportTicketResponse],
)
def list_support_tickets(
    status: TicketStatus | None = None,
    assigned_admin_id: uuid.UUID | None = None,
    unassigned: bool = False,
    user: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    return service.list_tickets(
        status=status,
        assigned_admin_id=assigned_admin_id,
        unassigned=unassigned,
    )


@router.get(
    "/{ticket_id}",
    response_model=SupportTicketResponse,
)
def get_support_ticket(
    ticket_id: uuid.UUID,
    user: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    return service.get_by_id_or_raise(ticket_id)


@router.patch(
    "/{ticket_id}/status",
    response_model=SupportTicketResponse,
)
def update_ticket_status(
    ticket_id: uuid.UUID,
    request: UpdateTicketStatusRequest,
    user: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    try:
        ticket = service.update_status(ticket_id, request.status)
    except InvalidTicketTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot move ticket from {exc.current} to {exc.target}",
        ) from exc

    session.commit()
    session.refresh(ticket)

    return ticket


@router.patch(
    "/{ticket_id}/assign",
    response_model=SupportTicketResponse,
)
def assign_support_ticket(
    ticket_id: uuid.UUID,
    request: AssignTicketRequest,
    user: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    admin = UserService(session).get_by_id_or_raise(
        request.admin_id,
    )

    try:
        ticket = service.assign_ticket(
            ticket_id=ticket_id,
            admin=admin,
        )
    except InvalidAssigneeError:
        raise HTTPException(
            status_code=400,
            detail="Tickets may only be assigned to admins.",
        )

    session.commit()
    session.refresh(ticket)

    return ticket


@router.patch(
    "/{ticket_id}/claim",
    response_model=SupportTicketResponse,
)
def claim_support_ticket(
    ticket_id: uuid.UUID,
    admin: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    try:
        ticket = service.claim_ticket(
            ticket_id=ticket_id,
            admin=admin,
        )
    except TicketAlreadyAssignedError:
        raise HTTPException(
            status_code=409,
            detail="Ticket has already been assigned.",
        )

    session.commit()
    session.refresh(ticket)

    return ticket


@router.patch(
    "/{ticket_id}/unassign",
    response_model=SupportTicketResponse,
)
def unassign_support_ticket(
    ticket_id: uuid.UUID,
    admin: User = Depends(require_role(SystemRole.admin)),
    session: Session = Depends(get_db),
):
    service = SupportTicketService(session)

    ticket = service.unassign_ticket(
        ticket_id=ticket_id,
    )

    session.commit()
    session.refresh(ticket)

    return ticket
