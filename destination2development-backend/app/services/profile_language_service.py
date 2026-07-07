from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.language import Language
from app.models.profile_language import (
    LanguageType,
    ProfileLanguage,
)


class LanguageNotFoundError(Exception):
    pass

class ProfileLanguageService:
    def __init__(self, session: Session):
        self.session = session

    def add_language(
        self,
        profile_id: uuid.UUID,
        language_id: uuid.UUID,
        language_type: LanguageType,
    ) -> ProfileLanguage:
        language = self.session.get(Language, language_id)
        if language is None:
            raise LanguageNotFoundError()

        stmt = select(ProfileLanguage).where(
            ProfileLanguage.profile_id == profile_id,
            ProfileLanguage.language_id == language_id,
            ProfileLanguage.type == language_type,
        )
        existing = self.session.scalar(stmt)
        if existing:
            return existing

        profile_language = ProfileLanguage(
            profile_id=profile_id,
            language_id=language_id,
            type=language_type,
        )
        self.session.add(profile_language)
        return profile_language

    def remove_language(
        self,
        profile_id: uuid.UUID,
        language_id: uuid.UUID,
        language_type: LanguageType,
    ) -> None:
        stmt = select(ProfileLanguage).where(
            ProfileLanguage.profile_id == profile_id,
            ProfileLanguage.language_id == language_id,
            ProfileLanguage.type == language_type,
        )
        profile_language = self.session.scalar(stmt)
        if profile_language:
            self.session.delete(profile_language)

    def get_profile_languages(
        self,
        profile_id: uuid.UUID,
    ) -> list[ProfileLanguage]:
        stmt = select(ProfileLanguage).where(
            ProfileLanguage.profile_id == profile_id,
        )
        return list(self.session.scalars(stmt))

    def get_by_type(
        self,
        profile_id: uuid.UUID,
        language_type: LanguageType,
    ) -> list[ProfileLanguage]:
        stmt = select(ProfileLanguage).where(
            ProfileLanguage.profile_id == profile_id,
            ProfileLanguage.type == language_type,
        )
        return list(self.session.scalars(stmt))