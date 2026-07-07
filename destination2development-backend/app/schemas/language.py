from __future__ import annotations

import uuid

from pydantic import BaseModel


class LanguageResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str

    model_config = {
        "from_attributes": True,
    }