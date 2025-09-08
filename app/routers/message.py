from uuid import UUID
from fastapi import APIRouter, Body, Depends
from app.dependencies import get_current_user, get_message_service
from app.enums.send_types import SenderType
from app.models.user import User
from app.schemas import message as message_schema
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Mensajes"])


@router.get(
    "/{session_id}",
    summary="Lista de mensajes",
    description="Mensajes filtrados por sesión",
    status_code=200,
    responses={
        200: {"description": "Lista de mensajes"},
        422: {"description": "Error de validación"},
    },
)
async def list_messages(
    session_id: UUID,
    _: User = Depends(get_current_user),
    params: message_schema.MessageFilters = Depends(),
    message_service: MessageService = Depends(get_message_service),
):
    return await message_service.message_list(session_id=session_id, params=params)


@router.post(
    "/",
    summary="Crear mensaje",
    status_code=200,
    response_model=message_schema.MessageCreationResponse,
    responses={
        200: {"description": "Mensaje enviado"},
        422: {"description": "Error de validación"},
    },
)
async def create_message(
    message: message_schema.MessageCreate,
    user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service),
):
    return await message_service.create_message(
        message_data=message,
        sender_id=user.id if message.sender_type == SenderType.user else None,
    )
