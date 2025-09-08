from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime


class LoginAttempt(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True)
    ip_address: str
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
