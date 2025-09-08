from functools import lru_cache
import jwt
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import db, connection_manager, task_manager
from app.core.connection_manager import ConnectionManager
from app.core.task_manager import TaskManager
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.message_service import MessageService
from app.services.auth_service import AuthService
from app.services.session_service import SessionService
from app.services.token_control_service import TokenControlService
from app.services.user_service import UserService
from app.settings import Settings, get_settings


def get_connection_manager() -> ConnectionManager:
    return connection_manager.manager


def get_task_manager() -> TaskManager:
    return task_manager.manager


async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    async with AsyncSession(db.engine) as session:
        service = AuthService(session=session)
        yield service


async def get_session_service() -> AsyncGenerator[SessionService, None]:
    async with AsyncSession(db.engine) as session:
        service = SessionService(manager=connection_manager.manager, session=session)
        yield service


async def get_message_service(
    manager: ConnectionManager = Depends(get_connection_manager),
) -> AsyncGenerator[MessageService, None]:
    async with AsyncSession(db.engine) as session:
        service = MessageService(manager=manager, session=session)
        yield service


async def get_user_service() -> AsyncGenerator[UserService, None]:
    async with AsyncSession(db.engine) as session:
        service = UserService(session=session)
        yield service


async def get_token_control_service() -> AsyncGenerator[TokenControlService, None]:
    async with AsyncSession(db.engine) as session:
        service = TokenControlService(session=session)
        yield service


async def get_audit_service() -> AsyncGenerator[AuditService, None]:
    async with AsyncSession(db.engine) as session:
        service = AuditService(session=session)
        yield service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    token_control_service: TokenControlService = Depends(get_token_control_service),
    settings: Settings = Depends(get_settings),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )

        if await token_control_service.is_token_revoked(jti=payload.get("jti")):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        user = await user_service.get_by_id(user_id=payload.get("sub"))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return current_user
