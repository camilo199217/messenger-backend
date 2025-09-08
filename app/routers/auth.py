from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.limiter import limiter
from app.dependencies import (
    get_audit_service,
    get_auth_service,
    get_token_control_service,
    oauth2_scheme,
)
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    AuthService,
)
from app.core.jwt import create_access_token
from app.services.audit_service import AuditService
from app.services.login_tracker import is_blocked, register_login_attempt
from app.services.token_control_service import TokenControlService
from app.settings import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    return await auth_service.create_user(user_data=user_data)


@limiter.limit("10/minute")
@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    username = form_data.username
    ip = request.client.host

    """ if is_blocked(username=username, ip=ip, settings=settings, session=session):
        await audit_event(
            request,
            session,
            action="login_blocked",
            success=False,
            username=username,
        )
        raise HTTPException(
            status_code=403,
            detail="Too many failed login attempts. Please wait a few minutes.",
        ) """

    user = await auth_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user:
        """ await audit_event(
            request, session, action="login_failed", success=False, username=username
        )

        register_login_attempt(username, ip, False, settings, session) """

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    """ register_login_attempt(username, ip, True, settings, session)

    await audit_event(
        request, session, action="login_success", success=True, username=username
    ) """

    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    token_control_service: TokenControlService = Depends(get_token_control_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    await token_control_service.revoke_token(token=token)
    await audit_service.audit_event(request=request, action="logout", success=True)
    return {"message": "Token revoked"}
