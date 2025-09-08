import uuid
from pydantic import BaseModel, Field

from app.enums.session_enum import SessionLevelCensorship
from app.schemas.pagination import PaginationParams


class CreateSession(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level_censorship: SessionLevelCensorship = Field(...)


class SessionDetail(BaseModel):
    id: uuid.UUID
    name: str


class SessionFilters(PaginationParams): ...
