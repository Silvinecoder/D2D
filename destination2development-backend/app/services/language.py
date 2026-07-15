from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.language import Language
from app.services.base import CRUDService


class LanguageNotFoundError(Exception):
    pass


class LanguageService(CRUDService[Language]):
    model = Language
    not_found_error = LanguageNotFoundError

    def get_by_code(self, code: str) -> Language | None:
        stmt = select(Language).where(Language.code == code.lower().strip())
        return self.session.scalar(stmt)

    def list_languages(self) -> list[Language]:
        stmt = select(Language).order_by(Language.name)
        return list(self.session.scalars(stmt))
