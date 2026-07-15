from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile_document import (
    DocumentType,
    ProfileDocument,
    VerificationStatus,
)
from app.models.user import User
from app.services.base import CRUDService, utcnow


class DocumentNotFoundError(Exception):
    pass


class DocumentAlreadyExistsError(Exception):
    pass


class InvalidDocumentStateError(Exception):
    pass


class ProfileDocumentService(CRUDService[ProfileDocument]):
    model = ProfileDocument
    not_found_error = DocumentNotFoundError

    def upload_document(
        self,
        user: User,
        document_type: DocumentType,
        file_path: str,
    ) -> ProfileDocument:
        stmt = select(ProfileDocument).where(
            ProfileDocument.user_id == user.id,
            ProfileDocument.document_type == document_type,
        )
        existing = self.session.execute(stmt).scalar_one_or_none()

        if existing:
            raise DocumentAlreadyExistsError()

        document = ProfileDocument(
            user_id=user.id,
            document_type=document_type,
            file_path=file_path,
            verification_status=VerificationStatus.pending,
        )
        self.session.add(document)

        return document

    def mark_in_review(self, document_id: uuid.UUID, reviewer: User) -> ProfileDocument:
        document = self.get_by_id_or_raise(document_id)

        if document.verification_status != VerificationStatus.pending:
            raise InvalidDocumentStateError()

        document.verification_status = VerificationStatus.in_review
        document.verified_by = reviewer.id

        return document

    def approve_document(
        self, document_id: uuid.UUID, reviewer: User
    ) -> ProfileDocument:
        document = self._transition_reviewable(document_id, reviewer)
        document.verification_status = VerificationStatus.approved
        return document

    def reject_document(
        self, document_id: uuid.UUID, reviewer: User
    ) -> ProfileDocument:
        document = self._transition_reviewable(document_id, reviewer)
        document.verification_status = VerificationStatus.rejected
        return document

    def _transition_reviewable(
        self, document_id: uuid.UUID, reviewer: User
    ) -> ProfileDocument:
        document = self.get_by_id_or_raise(document_id)

        if document.verification_status not in {
            VerificationStatus.pending,
            VerificationStatus.in_review,
        }:
            raise InvalidDocumentStateError()

        document.verified_by = reviewer.id
        document.verified_at = utcnow()

        return document

    def list_documents(
        self,
        user_id: uuid.UUID | None = None,
        status: VerificationStatus | None = None,
    ) -> list[ProfileDocument]:
        stmt = select(ProfileDocument)

        if user_id:
            stmt = stmt.where(ProfileDocument.user_id == user_id)

        if status:
            stmt = stmt.where(ProfileDocument.verification_status == status)

        return list(self.session.execute(stmt).scalars().all())
