import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException, status

from ..app.enums.send_types import SenderType
from ..app.enums.session_enum import SessionLevelCensorship
from ..app.schemas.message import MessageCreate, MessageFilters


# --- Fakes para el entorno de pruebas ---
class FakeMessage:
    id = "fake_id_column"
    content = "fake_content_column"
    sender_id = "fake_sender_id_column"
    session_id = "fake_session_id_column"
    sender_type = "fake_sender_type_column"
    title = "fake_title_column"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = kwargs.get("id", uuid4())
        self.content = kwargs.get("content", "Fake Content")
        self.sender_id = kwargs.get("sender_id", uuid4())
        self.session_id = kwargs.get("session_id", uuid4())
        self.sender_type = kwargs.get("sender_type", SenderType.user)
        self.title = kwargs.get("title", "Fake Title")


class FakeResult:
    def __init__(self, one_or_none=None, all_data=None):
        self._one_or_none = one_or_none
        self._all = all_data or []

    def one_or_none(self):
        return self._one_or_none

    def all(self):
        return self._all


class FakeSelect:
    def where(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self


class TestMessageService(unittest.IsolatedAsyncioTestCase):
    """Pruebas unitarias para MessageService"""

    async def asyncSetUp(self):
        import app.services.message_service as service_module

        # Patch del modelo Message, select y func
        service_module.Message = FakeMessage
        service_module.select = MagicMock(
            side_effect=lambda *args, **kwargs: FakeSelect()
        )
        service_module.func = MagicMock()

        # Mock de AsyncSession y ConnectionManager
        self.mock_session = AsyncMock()
        self.mock_manager = MagicMock()
        self.mock_manager.broadcast = AsyncMock()

        # Instancia del servicio
        self.service = service_module.MessageService(
            session=self.mock_session, manager=self.mock_manager
        )

        # Patch de profanity
        self.patcher = patch("app.services.message_service.profanity", autospec=True)
        self.mock_profanity = self.patcher.start()

    async def asyncTearDown(self):
        self.patcher.stop()

    def fake_session_data(self, level):
        return {"data": MagicMock(level_censorship=level)}

    async def test_create_message_low_censorship(self):
        """Debe crear mensaje sin censura en level LOW"""
        session_id = uuid4()
        sender_id = "user-id"
        message_data = MessageCreate(
            session_id=session_id,
            content="Hello world",
            sender_type=SenderType.user,
        )
        self.mock_manager.active_connections = {
            session_id: self.fake_session_data(SessionLevelCensorship.low)
        }
        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        self.mock_profanity.censor.return_value = "Hello world"
        self.mock_profanity.contains_profanity.return_value = False

        result = await self.service.create_message(
            sender_id=sender_id, message_data=message_data
        )

        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_awaited()
        self.mock_session.refresh.assert_awaited()
        self.mock_profanity.censor.assert_not_called()
        self.mock_profanity.contains_profanity.assert_not_called()
        self.assertIsInstance(result, FakeMessage)
        self.assertEqual(result.content, "Hello world")
        self.assertEqual(result.sender_type, SenderType.user)

    async def test_create_message_medium_censorship(self):
        """Debe censurar el contenido en level MEDIUM"""
        session_id = uuid4()
        sender_id = "user-id"
        message_data = MessageCreate(
            session_id=session_id,
            content="badword",
            sender_type=SenderType.user,
        )
        self.mock_manager.active_connections = {
            session_id: self.fake_session_data(SessionLevelCensorship.medium)
        }
        self.mock_profanity.censor.return_value = "****"
        self.mock_profanity.contains_profanity.return_value = False

        result = await self.service.create_message(
            sender_id=sender_id, message_data=message_data
        )

        self.mock_profanity.censor.assert_called_once_with("badword")
        self.assertEqual(result.content, "****")
        self.assertEqual(result.sender_type, SenderType.user)

    async def test_create_message_high_censorship_no_profanity(self):
        """No debe censurar ni rechazar mensaje limpio en HIGH"""
        session_id = uuid4()
        sender_id = "user-id"
        message_data = MessageCreate(
            session_id=session_id,
            content="good message",
            sender_type=SenderType.system,
        )
        self.mock_manager.active_connections = {
            session_id: self.fake_session_data(SessionLevelCensorship.high)
        }
        self.mock_profanity.contains_profanity.return_value = False

        result = await self.service.create_message(
            sender_id=sender_id, message_data=message_data
        )

        self.mock_profanity.contains_profanity.assert_called_once_with("good message")
        self.assertEqual(result.content, "good message")
        self.assertEqual(result.sender_type, SenderType.system)

    async def test_create_message_high_censorship_with_profanity(self):
        """Debe rechazar mensaje ofensivo en HIGH"""
        session_id = uuid4()
        sender_id = "user-id"
        message_data = MessageCreate(
            session_id=session_id,
            content="badword",
            sender_type=SenderType.user,
        )
        self.mock_manager.active_connections = {
            session_id: self.fake_session_data(SessionLevelCensorship.high)
        }
        self.mock_profanity.contains_profanity.return_value = True

        with self.assertRaises(HTTPException) as exc:
            await self.service.create_message(
                sender_id=sender_id, message_data=message_data
            )

        self.assertEqual(exc.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exc.exception.detail, "ofensive_content")

    async def test_create_message_session_not_found(self):
        """Debe lanzar error si la sesión no existe"""
        session_id = uuid4()
        sender_id = uuid4()
        message_data = MessageCreate(
            content="test",
            sender_type=SenderType.user,
            session_id=session_id,
        )
        self.mock_manager.active_connections = {}

        with self.assertRaises(HTTPException) as exc:
            await self.service.create_message(
                sender_id=sender_id, message_data=message_data
            )

        self.assertEqual(exc.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(exc.exception.detail, "session_not_found")

    async def test_message_list_success(self):
        """Debe listar mensajes correctamente"""
        session_id = uuid4()
        params = MessageFilters(
            page=1, size=2, search=None, sort_by=None, descending=None
        )
        fake_messages = [
            FakeMessage(content="M1", sender_type=SenderType.user),
            FakeMessage(content="M2", sender_type=SenderType.system),
        ]
        self.mock_session.exec.side_effect = [
            FakeResult(all_data=fake_messages),
            FakeResult(all_data=fake_messages),
        ]

        result = await self.service.message_list(session_id=session_id, params=params)

        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0].content, "M1")
        self.assertEqual(result["items"][0].sender_type, SenderType.user)
        self.assertEqual(result["items"][1].sender_type, SenderType.system)

    async def test_message_list_with_search_and_sort(self):
        """Debe aplicar search y sort en la consulta"""
        session_id = uuid4()
        params = MessageFilters(
            page=1, size=1, search="foo", sort_by="content", descending="DESC"
        )
        fake_messages = [FakeMessage(content="foo", sender_type=SenderType.user)]
        self.mock_session.exec.side_effect = [
            FakeResult(all_data=fake_messages),
            FakeResult(all_data=fake_messages),
        ]

        result = await self.service.message_list(session_id=session_id, params=params)

        self.assertEqual(result["total"], 1)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0].content, "foo")
        self.assertEqual(result["items"][0].sender_type, SenderType.user)
