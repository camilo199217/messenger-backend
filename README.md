# 💬 Messenger Backend

Backend de mensajería instantánea con control de sesiones, usuarios, mensajes y filtros de contenido ofensivo, desarrollado con **FastAPI** y **SQLModel**. Incluye autenticación JWT, control de intentos de login, auditoría de eventos y soporte para WebSockets.

## 🚀 Tecnologías Principales

- **Python 3.13.7**
- **FastAPI** (API REST y WebSocket)
- **SQLModel** (ORM sobre SQLAlchemy)
- **SQLite** (por defecto, configurable)
- **Pydantic** (validación de datos)
- **JWT** (autenticación)
- **Slowapi** (rate limiting)
- **Better Profanity** (filtro de palabras ofensivas)
- **WebSockets** (mensajería en tiempo real)

## ⚙️ Instalación y Ejecución

1. **Clona el repositorio y entra al directorio:**
   ```bash
   git clone <repo-url>
   cd messenger
   ```

2. **Instala dependencias con Poetry:**
   ```bash
   poetry install
   ```

3. **Configura variables de entorno en `.env`:**
   ```
   DATABASE_URL="sqlite+aiosqlite:///database.db"
   JWT_SECRET="tu_clave_secreta"
   ```

4. **Ejecuta la aplicación:**
   ```bash
   poetry run fastapi app/main.py

   # Modo desarrollo
   poetry run fastapi dev app/main.py
   ```

## 🧩 Estructura del Proyecto

- `app/main.py`: Punto de entrada de la API.
- `app/models/`: Modelos de base de datos (usuarios, sesiones, mensajes, etc).
- `app/schemas/`: Esquemas Pydantic para validación y serialización.
- `app/services/`: Lógica de negocio (usuarios, sesiones, mensajes, autenticación, etc).
- `app/routers/`: Endpoints de la API REST y WebSocket.
- `app/core/`: Utilidades, seguridad, conexión a base de datos, rate limiting, etc.
- `app/profanity_word_list.txt`: Lista personalizada de palabras ofensivas.
- `tests/`: Pruebas unitarias.

## 🔐 Funcionalidades

- **Registro e inicio de sesión** con JWT.
- **Control de intentos de login** y bloqueo temporal.
- **Gestión de usuarios, sesiones y mensajes**.
- **WebSocket** para mensajería en tiempo real por sesión.
- **Filtro de contenido ofensivo** configurable por nivel de censura.
- **Auditoría de eventos** (login, logout, etc).
- **Rate limiting** para proteger endpoints sensibles.

## 📚 Endpoints Principales

- `POST /auth/register`: Registro de usuario.
- `POST /auth/login`: Login y obtención de token JWT.
- `POST /auth/logout`: Revocación de token.
- `GET /sessions/`: Listado de sesiones.
- `POST /sessions/`: Crear nueva sesión.
- `GET /messages/{session_id}`: Listar mensajes de una sesión.
- `POST /messages/`: Enviar mensaje.
- `WS /ws/{session_id}/`: Conexión WebSocket a una sesión.

## 🧪 Pruebas

Ejecuta las pruebas con:
```bash
poetry run pytest
```

## 📝 Notas

- El filtro de palabras ofensivas se carga desde `app/profanity_word_list.txt`.
- El sistema soporta distintos niveles de censura por sesión (`low`, `medium`, `high`).
- Puedes cambiar la base de datos modificando `DATABASE_URL` en `.env`.

---
  
Autor: Juan Camilo Palacio Alvarez
