from datetime import datetime
from uuid import UUID, uuid4
from pydantic import model_validator
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from app.enums.send_types import SenderType


class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str
    timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de creación",
    )

    sender_type: SenderType = Field(default=SenderType.user)

    sender_id: UUID = Field(foreign_key="users.id")
    sender: "User" = Relationship(back_populates="messages")

    session_id: UUID = Field(foreign_key="sessions.id")
    session: "Session" = Relationship(back_populates="messages")

    __tablename__ = "messages"
    model_config = {"arbitrary_types_allowed": True}
