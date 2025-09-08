from typing import Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from app.models.session import Session
from app.schemas.session import CreateSession, SessionFilters
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.connection_manager import ConnectionManager


class SessionService:
    session: AsyncSession
    manager: ConnectionManager

    def __init__(self, session: AsyncSession, manager: ConnectionManager):
        self.session = session
        self.manager = manager

    async def create_session(
        self, *, created_by_id: UUID, session_data: CreateSession
    ) -> Session:
        """Crea una nueva sesión."""
        try:
            session = Session(**session_data.model_dump(), created_by_id=created_by_id)

            self.session.add(session)
            await self.session.commit()
            await self.session.refresh(session)

            self.manager.create_session(
                session=session,
            )
            return session
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="session_name_already_exists",
            )

    async def get_by_id(self, *, session_id: UUID) -> Union[Session | None]:
        stmt = select(Session).where(Session.id == session_id)
        result = await self.session.exec(stmt)

        return result.one_or_none()

    async def session_list(self, *, params: SessionFilters):
        """Lista todas las tareas."""
        offset = (params.page - 1) * params.size

        query = select(Session)

        total = await self.session.exec(select(Session))
        total_count = len(total.all())

        if params.search and params.search.strip():
            pattern = f"%{params.search.strip().lower()}%"
            query = query.filter(func.lower(Session.name).ilike(pattern))

        if params.sort_by and hasattr(Session, params.sort_by):
            if params.descending == "DESC":
                query = query.order_by(desc(params.sort_by))
            else:
                query = query.order_by(asc(params.sort_by))

        query = query.offset(offset)

        if params.size > 0:
            query = query.limit(params.size)

        result = await self.session.exec(query)
        items = result.all()

        return {"total": total_count, "items": items}
