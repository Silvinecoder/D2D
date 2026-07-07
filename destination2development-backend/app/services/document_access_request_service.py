from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_access_request import (
    DocumentAccessRequest,
    Status,
)
from app.models.user import User
from app.services.base_service import CRUDService, utcnow


class AccessRequestNotFoundError(Exception):
    pass


class AccessRequestAlreadyProcessedError(Exception):
    pass


class PendingAccessRequestAlreadyExistsError(Exception):
    pass


class DocumentAccessRequestService(CRUDService[DocumentAccessRequest]):
    model = DocumentAccessRequest
    not_found_error = AccessRequestNotFoundError

    def create_request(
        self, user: User, reason: str | None = None
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
            requested_at=utcnow(),
        )
        self.session.add(request)

        return request

    def approve_request(
        self, request_id: uuid.UUID, reviewer: User
    ) -> DocumentAccessRequest:
        return self._resolve_request(request_id, reviewer, Status.approved)

    def reject_request(
        self, request_id: uuid.UUID, reviewer: User
    ) -> DocumentAccessRequest:
        return self._resolve_request(request_id, reviewer, Status.rejected)

    def _resolve_request(
        self,
        request_id: uuid.UUID,
        reviewer: User,
        new_status: Status,
    ) -> DocumentAccessRequest:
        request = self.get_by_id_or_raise(request_id)

        if request.status != Status.pending:
            raise AccessRequestAlreadyProcessedError()

        request.status = new_status
        request.reviewed_by = reviewer.id
        request.reviewed_at = utcnow()

        return request

    def list_requests(
        self, status: Status | None = None
    ) -> list[DocumentAccessRequest]:
        stmt = select(DocumentAccessRequest)

        if status is not None:
            stmt = stmt.where(DocumentAccessRequest.status == status)

        return list(self.session.scalars(stmt))
