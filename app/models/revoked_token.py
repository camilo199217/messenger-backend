from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime


class RevokedToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    jti: str = Field(index=True, unique=True)
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
