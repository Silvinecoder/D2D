from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.language import Language


class LanguageNotFoundError(Exception):
    pass


class LanguageService:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get_by_id(
        self,
        language_id: uuid.UUID,
    ) -> Language | None:
        return self.session.get(
            Language,
            language_id,
        )

    def get_by_id_or_raise(
        self,
        language_id: uuid.UUID,
    ) -> Language:
        language = self.get_by_id(language_id)

        if language is None:
            raise LanguageNotFoundError()

        return language

    def get_by_code(
        self,
        code: str,
    ) -> Language | None:
        stmt = select(Language).where(
            Language.code == code.lower().strip(),
        )

        return self.session.scalar(stmt)

    def list_languages(
        self,
    ) -> list[Language]:
        stmt = select(Language).order_by(
            Language.name,
        )

        return list(self.session.scalars(stmt))
