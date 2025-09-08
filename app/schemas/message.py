from datetime import datetime
import uuid
from pydantic import BaseModel, Field

from app.enums.send_types import SenderType
from app.schemas.pagination import PaginationParams


class MessageCreate(BaseModel):
    content: str = Field(..., max_length=300)
    sender_type: SenderType
    session_id: uuid.UUID

    model_config = {
        "arbitrary_types_allowed": True,
    }


class MessageDetail(BaseModel):
    id: uuid.UUID
    content: str
    session_id: uuid.UUID
    timestamp: datetime
    sender_id: uuid.UUID


class MessageFilters(PaginationParams): ...
