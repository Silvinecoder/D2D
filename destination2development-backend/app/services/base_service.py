from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


def utcnow() -> datetime:
    return datetime.now(UTC)


class CRUDService(Generic[ModelType]):
    """Base class for services that fetch a single model by primary key.

    Subclasses must set `model` (the SQLAlchemy model) and `not_found_error`
    (the exception to raise when a lookup fails).

    `get_by_id` returns None on a miss; `get_by_id_or_raise` raises
    `not_found_error`. Override `get_by_id` in a subclass if you need it to
    raise instead (see UserService).
    """

    model: type[ModelType]
    not_found_error: type[Exception]

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, entity_id: uuid.UUID) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def get_by_id_or_raise(self, entity_id: uuid.UUID) -> ModelType:
        entity = self.get_by_id(entity_id)
        if entity is None:
            raise self.not_found_error()
        return entity
