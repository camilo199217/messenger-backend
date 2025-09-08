from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from datetime import datetime


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=True)
    is_deleted: bool = Field(
        default=False, nullable=True
    )  # Indicates if the record is logically deleted

    def save(self):
        """Method to save the model instance."""
        self.updated_at = datetime.utcnow()
        # Logic to save the instance to the database would go here
        # For example, using a session to add and commit the instance
        # session.add(self)
        # session.commit()
