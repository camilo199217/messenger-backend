from uuid import UUID
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.connection_manager import ConnectionManager
from app.dependencies import get_connection_manager, get_session_service
from app.models.message import Message
from app.services.session_service import SessionService

router = APIRouter()


@router.websocket("/ws/{session_id}/")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    manager: ConnectionManager = Depends(get_connection_manager),
    session_service: SessionService = Depends(get_session_service),
):
    session = await session_service.get_by_id(session_id=session_id)

    if not session:
        raise WebSocketDisconnect(code=1008, reason="session not found")

    try:
        await manager.connect(websocket=websocket, session=session)

        while True:
            data = await websocket.receive_json()
            message = Message(**data, session_id=session_id)
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
