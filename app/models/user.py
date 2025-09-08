from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint
from typing import Optional


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password: Optional[str]
    full_name: Optional[str] = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sessions: list["Session"] = Relationship(back_populates="created_by")

    messages: list["Message"] = Relationship(back_populates="sender")

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_email"),)
