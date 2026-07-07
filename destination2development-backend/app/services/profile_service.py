from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.profile_document import DocumentType
from app.models.user import User
from app.services.profile_document_service import (
    DocumentNotFoundError,
    ProfileDocumentService,
)


class ProfileNotFoundError(Exception):
    pass


class ProfileAlreadyExistsError(Exception):
    pass


class InvalidAvatarDocumentError(Exception):
    pass


class ProfileService:
    def __init__(self, session: Session):
        self.session = session

    def create_profile(
        self,
        user: User,
        *,
        qualification: str | None = None,
        avatar_document_id: uuid.UUID | None = None,
        date_of_birth: date | None = None,
        gender: str | None = None,
        city: str | None = None,
        education_level: str | None = None,
    ) -> Profile:

        existing = self.get_by_user_id(user.id)

        if existing:
            raise ProfileAlreadyExistsError()

        profile = Profile(
            user_id=user.id,
            qualification=qualification,
            date_of_birth=date_of_birth,
            gender=gender,
            city=city,
            education_level=education_level,
        )

        if avatar_document_id is not None:
            try:
                document = ProfileDocumentService(
                    self.session,
                ).get_by_id_or_raise(
                    avatar_document_id,
                )
            except DocumentNotFoundError:
                raise InvalidAvatarDocumentError()

            if (
                document.user_id != user.id
                or document.document_type != DocumentType.profile_photo
            ):
                raise InvalidAvatarDocumentError()

            profile.avatar_document_id = avatar_document_id

        self.session.add(profile)
        self.session.flush()

        return profile

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> Profile | None:

        stmt = select(Profile).where(
            Profile.user_id == user_id,
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_profile_or_raise(
        self,
        user_id: uuid.UUID,
    ) -> Profile:

        profile = self.get_by_user_id(user_id)

        if profile is None:
            raise ProfileNotFoundError()

        return profile

    def update_profile(
        self,
        user_id: uuid.UUID,
        *,
        qualification: str | None = None,
        avatar_document_id: uuid.UUID | None = None,
        date_of_birth: date | None = None,
        gender: str | None = None,
        city: str | None = None,
        education_level: str | None = None,
    ) -> Profile:

        profile = self.get_profile_or_raise(user_id)

        if qualification is not None:
            profile.qualification = qualification

        if avatar_document_id is not None:
            try:
                document = ProfileDocumentService(
                    self.session,
                ).get_by_id_or_raise(
                    avatar_document_id,
                )
            except DocumentNotFoundError:
                raise InvalidAvatarDocumentError()

            if (
                document.user_id != user_id
                or document.document_type != DocumentType.profile_photo
            ):
                raise InvalidAvatarDocumentError()

            profile.avatar_document_id = avatar_document_id

        if date_of_birth is not None:
            profile.date_of_birth = date_of_birth

        if gender is not None:
            profile.gender = gender

        if city is not None:
            profile.city = city

        if education_level is not None:
            profile.education_level = education_level

        return profile
