from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# 🎯 Schema para crear usuarios (input POST)
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., max_length=100)
    password: str


# ✏️ Schema para actualizar usuarios (input PATCH / PUT)
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    full_name: Optional[str] = Field(max_length=100)


# 👀 Schema para leer usuarios (output GET)
class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = Field(max_length=100)
