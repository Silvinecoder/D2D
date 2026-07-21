from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import (
    AccountStatus,
    SystemRole,
    AccountType,
    User,
)
from app.schemas.user_auth0 import Auth0User
from app.services.base import CRUDService, utcnow


class AccountNotDeactivatedError(Exception):
    pass


class AccountNotLockedError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserService(CRUDService[User]):
    model = User
    not_found_error = UserNotFoundError

    def get_by_id(self, user_id: uuid.UUID) -> User:
        user = self.session.get(User, user_id)

        if not user:
            raise UserNotFoundError()

        return user

    def get_by_auth0_id(
        self,
        auth0_id: str,
    ) -> User | None:
        stmt = select(User).where(
            User.auth0_id == auth0_id,
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_all_users(self) -> list[User]:
        stmt = select(User).order_by(User.name)

        return list(self.session.scalars(stmt))

    def _update_user(
        self,
        user_id: uuid.UUID,
        **changes,
    ) -> User:
        user = self.get_by_id(user_id)

        for field, value in changes.items():
            setattr(user, field, value)

        return user

    # -------------------
    # Authentication
    # -------------------

    def get_or_create_auth0_user(
        self,
        auth0_user: Auth0User,
    ) -> User:
        user = self.get_by_auth0_id(
            auth0_user.auth0_id,
        )

        if user:
            user.last_login_at = utcnow()
            return user

        user = User(
            auth0_id=auth0_user.auth0_id,
            email=auth0_user.email,
            name=auth0_user.name,
            account_status=AccountStatus.active,
            system_role=SystemRole.user,
            account_type=None,
            last_login_at=utcnow(),
        )

        self.session.add(user)
        self.session.flush()

        return user

    def set_account_type(
        self,
        user_id: uuid.UUID,
        account_type: AccountType,
    ) -> User:
        return self._update_user(
            user_id,
            account_type=account_type,
        )

    # -------------------
    # Profile updates
    # -------------------

    def update_user_name(
        self,
        user_id: uuid.UUID,
        name: str,
    ) -> User:
        return self._update_user(
            user_id,
            name=name,
        )

    def update_user_email(
        self,
        user_id: uuid.UUID,
        email: str,
    ) -> User:
        return self._update_user(
            user_id,
            email=email,
        )

    def set_role(
        self,
        user_id: uuid.UUID,
        role: SystemRole,
    ) -> User:
        return self._update_user(
            user_id,
            system_role=role,
        )

    # -------------------
    # Account lifecycle
    # -------------------

    def lock_user(
        self,
        user_id: uuid.UUID,
    ) -> User:
        return self._update_user(
            user_id,
            account_status=AccountStatus.locked,
        )

    def deactivate_account(
        self,
        user_id: uuid.UUID,
    ) -> User:
        user = self.get_by_id(user_id)

        user.account_status = AccountStatus.deactivated
        user.deactivated_at = utcnow()

        return user

    def restore_account(self, user_id: uuid.UUID) -> User:
        user = self.get_by_id(user_id)

        if user.account_status != AccountStatus.deactivated:
            raise AccountNotDeactivatedError()

        user.account_status = AccountStatus.active
        user.deactivated_at = None

        return user

    def permanently_delete(
        self,
        user_id: uuid.UUID,
    ) -> User:
        user = self.get_by_id(user_id)

        self.session.delete(user)

        return user
