from __future__ import annotations

import uuid
from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile_document import (
    ProfileDocument,
    DocumentType,
    VerificationStatus,
)
from app.models.user import User


class DocumentNotFoundError(Exception):
    pass


class DocumentAlreadyExistsError(Exception):
    pass


class InvalidDocumentStateError(Exception):
    pass


class ProfileDocumentService:
    def __init__(self, session: Session):
        self.session = session

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

    def get_by_id(
        self,
        document_id: uuid.UUID,
    ) -> ProfileDocument | None:
        return self.session.get(ProfileDocument, document_id)

    def get_by_id_or_raise(
        self,
        document_id: uuid.UUID,
    ) -> ProfileDocument:

        document = self.get_by_id(document_id)

        if document is None:
            raise DocumentNotFoundError()

        return document

    def mark_in_review(
        self,
        document_id: uuid.UUID,
        reviewer: User,
    ) -> ProfileDocument:

        document = self.get_by_id_or_raise(document_id)

        if document.verification_status != VerificationStatus.pending:
            raise InvalidDocumentStateError()

        document.verification_status = VerificationStatus.in_review
        document.verified_by = reviewer.id

        return document

    def approve_document(
        self,
        document_id: uuid.UUID,
        reviewer: User,
    ) -> ProfileDocument:

        document = self.get_by_id_or_raise(document_id)

        if document.verification_status not in {
            VerificationStatus.pending,
            VerificationStatus.in_review,
        }:
            raise InvalidDocumentStateError()

        document.verification_status = VerificationStatus.approved
        document.verified_by = reviewer.id
        document.verified_at = datetime.now(UTC)

        return document

    def reject_document(
        self,
        document_id: uuid.UUID,
        reviewer: User,
    ) -> ProfileDocument:

        document = self.get_by_id_or_raise(document_id)

        if document.verification_status not in {
            VerificationStatus.pending,
            VerificationStatus.in_review,
        }:
            raise InvalidDocumentStateError()

        document.verification_status = VerificationStatus.rejected
        document.verified_by = reviewer.id
        document.verified_at = datetime.now(UTC)

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
