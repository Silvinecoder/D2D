from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import (
    AccountStatus,
    User,
)
from app.models.user_unlock_request import (
    UnlockRequestStatus,
    UserUnlockRequest,
)
from app.services.base_service import CRUDService


class UnlockRequestNotFoundError(Exception):
    pass


class UserUnlockRequestService(CRUDService[UserUnlockRequest]):
    model = UserUnlockRequest
    not_found_error = UnlockRequestNotFoundError

    def create_request(self, user: User, message: str) -> UserUnlockRequest:
        stmt = select(UserUnlockRequest).where(
            UserUnlockRequest.user_id == user.id,
            UserUnlockRequest.status == UnlockRequestStatus.pending,
        )
        existing = self.session.scalar(stmt)

        if existing:
            return existing

        request = UserUnlockRequest(
            user_id=user.id,
            message=message,
        )
        self.session.add(request)

        return request

    def get_pending_requests(self) -> list[UserUnlockRequest]:
        stmt = (
            select(UserUnlockRequest)
            .where(UserUnlockRequest.status == UnlockRequestStatus.pending)
            .order_by(UserUnlockRequest.created_at)
        )
        return list(self.session.scalars(stmt))

    def approve_request(self, request_id: uuid.UUID) -> UserUnlockRequest:
        request = self.get_by_id_or_raise(request_id)
        request.status = UnlockRequestStatus.approved
        request.user.account_status = AccountStatus.active
        return request

    def reject_request(self, request_id: uuid.UUID) -> UserUnlockRequest:
        request = self.get_by_id_or_raise(request_id)
        request.status = UnlockRequestStatus.rejected
        return request
