from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.services.profile_document import ProfileDocumentService
from app.services.user import UserService
from app.services.user_auth0 import Auth0Service


class AccountDeletionService:
    """Coordinates account deletion workflows."""

    def __init__(self, session: Session):
        self.users = UserService(session)
        self.documents = ProfileDocumentService(session)
        self.auth0 = Auth0Service()

    def deactivate(self, user_id: uuid.UUID) -> User:
        """
        User requests account deletion.

        The account is only deactivated so it can be restored later.
        Auth0 is intentionally left untouched.
        """
        user = self.users.deactivate_account(user_id)

        self.documents.remove_optional_profile_documents(user_id)

        return user

    def restore(self, user_id: uuid.UUID) -> User:
        """
        Restore a previously deactivated account.
        """
        return self.users.restore_account(user_id)

    def permanently_delete(self, user_id: uuid.UUID) -> User:
        """
        Permanently remove the account.

        This method is intended to be called only from an
        admin-protected endpoint.
        """
        user = self.users.get_by_id(user_id)

        self.documents.remove_optional_profile_documents(user_id)

        self.auth0.delete_user(user.auth0_id)

        return self.users.permanently_delete(user_id)
