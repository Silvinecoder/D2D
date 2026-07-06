from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_access_request import (
    DocumentAccessRequest,
    Status,
)
from app.models.user import User


class AccessRequestNotFoundError(Exception):
    pass


class AccessRequestAlreadyProcessedError(Exception):
    pass


class PendingAccessRequestAlreadyExistsError(Exception):
    pass


class DocumentAccessRequestService:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def create_request(
        self,
        user: User,
        reason: str | None = None,
    ) -> DocumentAccessRequest:

        stmt = select(DocumentAccessRequest).where(
            DocumentAccessRequest.user_id == user.id,
            DocumentAccessRequest.status == Status.pending,
        )

        existing = self.session.scalar(stmt)

        if existing:
            raise PendingAccessRequestAlreadyExistsError()

        request = DocumentAccessRequest(
            user_id=user.id,
            reason=reason,
            status=Status.pending,
            requested_at=datetime.now(UTC),
        )

        self.session.add(request)

        return request

    def get_by_id(
        self,
        request_id: uuid.UUID,
    ) -> DocumentAccessRequest | None:

        return self.session.get(
            DocumentAccessRequest,
            request_id,
        )

    def get_by_id_or_raise(
        self,
        request_id: uuid.UUID,
    ) -> DocumentAccessRequest:

        request = self.get_by_id(request_id)

        if request is None:
            raise AccessRequestNotFoundError()

        return request

    def approve_request(
        self,
        request_id: uuid.UUID,
        reviewer: User,
    ) -> DocumentAccessRequest:

        request = self.get_by_id_or_raise(request_id)

        if request.status != Status.pending:
            raise AccessRequestAlreadyProcessedError()

        request.status = Status.approved
        request.reviewed_by = reviewer.id
        request.reviewed_at = datetime.now(UTC)

        return request

    def reject_request(
        self,
        request_id: uuid.UUID,
        reviewer: User,
    ) -> DocumentAccessRequest:

        request = self.get_by_id_or_raise(request_id)

        if request.status != Status.pending:
            raise AccessRequestAlreadyProcessedError()

        request.status = Status.rejected
        request.reviewed_by = reviewer.id
        request.reviewed_at = datetime.now(UTC)

        return request

    def list_requests(
        self,
        status: Status | None = None,
    ) -> list[DocumentAccessRequest]:

        stmt = select(DocumentAccessRequest)

        if status is not None:
            stmt = stmt.where(
                DocumentAccessRequest.status == status,
            )

        return list(self.session.scalars(stmt))
