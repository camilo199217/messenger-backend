from typing import AsyncGenerator
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.settings import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False}
engine = create_async_engine(settings.database_url, connect_args=connect_args)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency for FastAPI routes
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


# Create tables at startup
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
