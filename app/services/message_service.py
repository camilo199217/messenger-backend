import asyncio
from typing import Union
from uuid import UUID
from better_profanity import profanity
from sqlmodel import asc, desc, func, select
from app.enums.session_enum import SessionLevelCensorship
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageFilters
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.connection_manager import ConnectionManager
from fastapi import status
from fastapi.exceptions import HTTPException


class MessageService:
    session: AsyncSession
    manager: ConnectionManager

    def __init__(self, session: AsyncSession, manager: ConnectionManager):
        self.session = session
        self.manager = manager

    async def create_message(
        self, *, sender_id: Union[str, None], message_data: MessageCreate
    ) -> dict:
        """Crea un nuevo mensaje."""
        message = Message(**message_data.model_dump(), sender_id=sender_id)

        session = None

        if message_data.session_id in self.manager.active_connections:
            session = self.manager.active_connections[message_data.session_id]["data"]

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="session_not_found"
            )

        if session.level_censorship == SessionLevelCensorship.medium:
            message.content = profanity.censor(message.content)

        if session.level_censorship == SessionLevelCensorship.high:
            if profanity.contains_profanity(message.content):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ofensive_content",
                )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        asyncio.create_task(self.manager.broadcast(message=message))

        return {
            "status": "success",
            "data": {
                "message_id": message.id,
                "session_id": session.id,
                "content": message.content,
                "timestamp": message.timestamp,
                "sender": message.sender_type,
                "metadata": {
                    "word_count": len(message.content.split()),
                    "character_count": len(message.content),
                    "processed_at": message.timestamp,
                },
            },
        }

    async def message_list(self, *, session_id: UUID, params: MessageFilters):
        """Lista todas las tareas."""
        offset = (params.page - 1) * params.size

        query = select(Message)

        total = await self.session.exec(
            select(Message).where(Message.session_id == session_id)
        )
        total_count = len(total.all())

        if params.search and params.search.strip():
            pattern = f"%{params.search.strip().lower()}%"
            query = query.filter(func.lower(Message.content).ilike(pattern))

        if params.sort_by:
            if hasattr(Message, params.sort_by):
                if params.descending == "DESC":
                    query = query.order_by(desc(params.sort_by))
                else:
                    query = query.order_by(asc(params.sort_by))

        query = query.offset(offset).limit(params.size)
        result = await self.session.exec(query)
        items = result.all()

        return {"total": total_count, "items": items}
