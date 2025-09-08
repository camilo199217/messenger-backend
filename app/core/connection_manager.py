import asyncio
from typing import Any, Dict, List
from uuid import UUID
from fastapi import WebSocket

from app.models.message import Message
from app.models.session import Session


class ConnectionManager:
    active_connections: Dict[str, Dict[str, Any | List[Any]]]

    def __init__(self):
        # Diccionario: session_id -> lista de conexiones WebSocket
        self.active_connections = {}

    async def connect(
        self,
        *,
        websocket: WebSocket,
        session: Session,
    ):
        await websocket.accept()
        if session.id not in self.active_connections:
            self.active_connections[session.id] = {"data": session, "connections": []}
        self.active_connections[session.id]["connections"].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: UUID):
        if session_id in self.active_connections:
            self.active_connections[session_id]["connections"].remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def load_sessions(self): ...

    def create_session(self, *, session: Session):
        self.active_connections[session.id] = {"data": session, "connections": []}

    async def broadcast(self, *, message: Message):
        """Enviar a todos los sockets en una sesión."""
        # await asyncio.sleep(5) -> Simular servidor lento
        if self.active_connections[message.session_id]:
            for connection in self.active_connections[message.session_id][
                "connections"
            ]:
                await connection.send_json(
                    message.model_dump_json(exclude=["session_id"])
                )


manager = ConnectionManager()
