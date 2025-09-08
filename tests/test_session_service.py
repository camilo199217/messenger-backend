import unittest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.enums.session_enum import SessionLevelCensorship
from app.services.session_service import SessionService
from app.schemas.session import CreateSession, SessionFilters


class TestSessionService(unittest.IsolatedAsyncioTestCase):
    """Pruebas unitarias para SessionService"""

    class FakeSession:
        """Modelo fake para evitar mapper de SQLAlchemy"""

        # atributos de clase que imitan columnas
        id = "fake_id_column"
        name = "fake_name_column"

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.id = kwargs.get("id", uuid4())
            self.name = kwargs.get("name", "Fake Name")
            self.level_censorship = kwargs.get(
                "level_censorship", SessionLevelCensorship.low
            )
            self.created_by_id = kwargs.get("created_by_id", uuid4())

    class FakeResult:
        """Fake de Result para simular .one_or_none() y .all()"""

        def __init__(self, one_or_none=None, all_data=None):
            self._one_or_none = one_or_none
            self._all = all_data or []

        def one_or_none(self):
            return self._one_or_none

        def all(self):
            return self._all

    class FakeSelect:
        """Fake que imita el query builder de SQLAlchemy"""

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

    async def asyncSetUp(self):
        import app.services.session_service as service_module

        # Patch del modelo Session
        service_module.Session = self.FakeSession

        # Patch de select y func para que no ejecuten SQLAlchemy real
        service_module.select = MagicMock(
            side_effect=lambda *args, **kwargs: self.FakeSelect()
        )
        service_module.func = MagicMock()

        # Mock de AsyncSession y ConnectionManager
        self.mock_session = AsyncMock()
        self.mock_manager = MagicMock()

        self.service = SessionService(
            session=self.mock_session, manager=self.mock_manager
        )

    async def test_create_session_success(self):
        """Debe crear una sesión correctamente"""
        user_id = uuid4()
        session_data = CreateSession(
            name="Test Session",
            level_censorship=SessionLevelCensorship.low,
        )

        self.mock_session.add = MagicMock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()

        result = await self.service.create_session(
            created_by_id=user_id, session_data=session_data
        )

        self.assertEqual(result.name, "Test Session")
        self.assertEqual(result.created_by_id, user_id)
        self.mock_manager.create_session.assert_called_once()

    async def test_create_session_integrity_error(self):
        """Debe lanzar HTTPException si el nombre ya existe"""
        user_id = uuid4()
        session_data = CreateSession(
            name="Duplicada",
            level_censorship=SessionLevelCensorship.low,
        )

        self.mock_session.add = MagicMock()
        self.mock_session.commit.side_effect = IntegrityError(
            "UNIQUE constraint failed", None, None
        )

        with self.assertRaises(HTTPException) as context:
            await self.service.create_session(
                created_by_id=user_id, session_data=session_data
            )

        self.assertEqual(
            context.exception.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        self.assertEqual(context.exception.detail, "session_name_already_exists")

    async def test_get_by_id_found(self):
        """Debe retornar la sesión si existe"""
        session_id = uuid4()
        fake = self.FakeSession(id=session_id, name="Encontrada")

        self.mock_session.exec.return_value = self.FakeResult(one_or_none=fake)

        result = await self.service.get_by_id(session_id=session_id)

        self.assertEqual(result.name, "Encontrada")

    async def test_get_by_id_not_found(self):
        """Debe retornar None si la sesión no existe"""
        self.mock_session.exec.return_value = self.FakeResult(one_or_none=None)

        result = await self.service.get_by_id(session_id=uuid4())

        self.assertIsNone(result)

    async def test_session_list_success(self):
        """Debe listar sesiones correctamente"""
        filters = SessionFilters(
            page=1, size=2, search=None, sort_by=None, descending=None
        )

        fake_sessions = [
            self.FakeSession(name="S1"),
            self.FakeSession(name="S2"),
        ]

        self.mock_session.exec.side_effect = [
            self.FakeResult(all_data=fake_sessions),  # total
            self.FakeResult(all_data=fake_sessions),  # query paginada
        ]

        result = await self.service.session_list(params=filters)

        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0].name, "S1")
