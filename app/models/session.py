from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

from app.enums.session_enum import SessionLevelCensorship


class Session(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(min_length=1, max_length=100, unique=True)

    level_censorship: Optional[SessionLevelCensorship] = Field(
        default=SessionLevelCensorship.low
    )

    created_by_id: UUID = Field(foreign_key="users.id")
    created_by: "User" = Relationship(back_populates="sessions")

    messages: list["Message"] = Relationship(back_populates="session")

    __tablename__ = "sessions"
    model_config = {
        "arbitrary_types_allowed": True,
    }
