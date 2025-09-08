from typing import Union
from uuid import UUID
from sqlmodel import select
from app.models.user import User
from app.schemas.user import UserCreate
from sqlmodel.ext.asyncio.session import AsyncSession


class UserService:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, *, user_id: str) -> Union[User | None]:
        stmt = select(User).where(User.id == UUID(user_id))
        result = await self.session.exec(stmt)

        return result.one_or_none()

    async def get_by_email(self, *, email: str) -> Union[User | None]:
        stmt = select(User).where(User.email == email)
        result = await self.session.exec(stmt)

        return result.one_or_none()

    async def get_or_create_user(self, *, user_data: UserCreate) -> User:
        user = self.get_by_email(email=user_data.email)

        if not user:
            user = User(**user_data)
            await self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        return user
