from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, get_session_service
from app.models.user import User
from app.schemas import session as session_schema
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sesiones"])


@router.get(
    "/",
    summary="Lista de sesiones",
    status_code=200,
    responses={
        200: {"description": "Lista de mensajes"},
        422: {"description": "Error de validación"},
    },
)
async def session_list(
    params: session_schema.SessionFilters = Depends(),
    _: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.session_list(params=params)


@router.post(
    "/",
    summary="Crear sesión",
    description="Al crear una sesión de manera exitosa se crea en el websocket",
    status_code=200,
    response_model=session_schema.SessionDetail,
    responses={
        200: {"description": "Sesión creada"},
        422: {"description": "Error de validación"},
    },
)
async def create_session(
    session: session_schema.CreateSession,
    user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    return await session_service.create_session(
        session_data=session, created_by_id=user.id
    )
