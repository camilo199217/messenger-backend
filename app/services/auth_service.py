from typing import Union
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.services.user_service import UserService
from app.settings import get_settings
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from sqlmodel.ext.asyncio.session import AsyncSession

settings = get_settings()


class AuthService:
    session: AsyncSession
    user_service: UserService

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = UserService(session=session)

    async def create_user(self, *, user_data: UserCreate) -> User:
        try:
            user_data.password = get_password_hash(user_data.password)
            user_obj = {**user_data.model_dump()}
            user = User(**user_obj)

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            # Send welcome email to activate account
            # This is a placeholder for actual email sending logic
            print(f"Sending welcome email to {user_data.email}...")

            return user
        except IntegrityError as e:
            raise e
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error creating user: {str(e)}",
            )

    async def authenticate_user(
        self, *, email: str, password: str
    ) -> Union[User | None]:
        user = await self.user_service.get_by_email(email=email)

        if not user:
            return None

        if not user.password:
            return None

        if not verify_password(password, user.password):
            return None

        return user
