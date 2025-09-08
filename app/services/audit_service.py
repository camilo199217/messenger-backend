from app.models.audit_event import AuditEvent
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Request


class AuditService:
    session: AsyncSession

    def __init__(self, *, session: AsyncSession):
        self.session = session

    async def audit_event(
        self, *, request: Request, action: str, success: bool, username: str = None
    ):
        ip = request.client.host
        user_agent = request.headers.get("user-agent")
        endpoint = request.url.path
        method = request.method

        event = AuditEvent(
            username=username,
            ip_address=ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            action=action,
            success=success,
        )
        await self.session.add(event)
        await self.session.commit()
