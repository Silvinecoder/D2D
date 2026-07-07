from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import (
    AccountStatus,
    SystemRole,
    User,
)
from app.schemas.user_auth0 import Auth0User


class UserNotFoundError(Exception):
    pass


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def _now(self):
        return datetime.now(UTC)

    def _default_name(self, email: str):
        return email.split("@", 1)[0]

    def get_or_create_auth0_user(self, auth0_user: Auth0User) -> User:
        user = self.get_by_auth0_id(auth0_user.auth0_id)

        if user:
            user.last_login_at = self._now()
            return user

        user = User(
            auth0_id=auth0_user.auth0_id,
            email=auth0_user.email,
            name=auth0_user.name,
            account_status=AccountStatus.active,
            system_role=SystemRole.user,
            last_login_at=self._now(),
        )
        self.session.add(user)
        self.session.flush()

        return user

    def get_by_auth0_id(self, auth0_id: str):
        stmt = select(User).where(User.auth0_id == auth0_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: uuid.UUID):
        user = self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def get_all_users(self):
        stmt = select(User).order_by(User.name)
        return list(self.session.scalars(stmt))

    def update_user_name(self, user_id: uuid.UUID, name: str) -> User:
        user = self.get_by_id(user_id)
        user.name = name
        return user

    def update_user_email(self, user_id: uuid.UUID, email: str) -> User:
        user = self.get_by_id(user_id)
        user.email = email
        return user

    def set_role(self, user_id: uuid.UUID, role: SystemRole) -> User:
        user = self.get_by_id(user_id)
        user.system_role = role
        return user

    def lock_user(self, user_id: uuid.UUID) -> User:
        user = self.get_by_id(user_id)
        user.account_status = AccountStatus.locked
        return user

    def schedule_deletion(self, user_id: uuid.UUID) -> User:
        user = self.get_by_id(user_id)
        now = self._now()
        user.deactivated_at = now
        user.scheduled_deletion_at = now + timedelta(days=30)
        return user

    def restore_user(self, user_id: uuid.UUID) -> User:
        user = self.get_by_id(user_id)
        user.deactivated_at = None
        user.scheduled_deletion_at = None
        user.deleted_at = None
        # Previously left untouched, so a locked or
        # pending-deletion account "restored" by an admin stayed
        # locked/pending forever. Restoring should mean usable again.
        user.account_status = AccountStatus.active
        return user

    def get_users_ready_for_deletion(self) -> list[User]:
        stmt = select(User).where(User.scheduled_deletion_at <= self._now())
        return list(self.session.scalars(stmt))

    def permanently_delete_user(self, user_id: uuid.UUID):
        user = self.get_by_id(user_id)
        self.session.delete(user)
