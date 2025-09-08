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
   git clone https://github.com/camilo199217/messenger-backend
   cd messenger-backend
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
   poetry run fastapi run app/main.py

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

## 🔌 Conexión WebSocket

Puedes conectarte al WebSocket usando la URL:

```
ws://localhost:8000/ws/{session_id}/
```

Reemplaza `{session_id}` por el ID de la sesión a la que deseas unirte. El WebSocket requiere autenticación JWT (token en el parámetro de conexión o encabezado según implementación).

Para probar la conexión puedes usar herramientas como:

- [Piehost WebSocket Tester](https://piehost.com/websocket-tester)
- [websocat](https://github.com/vi/websocat) (CLI)

Ejemplo de payload para enviar mensajes:

```json
{
   "content": "Hola mundo",
   "sender_type": "user"
}
```

## 🧪 Pruebas

Ejecuta las pruebas con:
```bash
poetry run pytest
```

## 🧹 Linting con Ruff

Este proyecto utiliza [Ruff](https://docs.astral.sh/ruff/) para el formateo y análisis estático de código Python. Puedes ejecutar Ruff con:

```bash
poetry run ruff check .
```

Para corregir automáticamente problemas de formato:

```bash
poetry run ruff check . --fix
```

La configuración se encuentra en `ruff.toml`.

## 📝 Notas

- El filtro de palabras ofensivas se carga desde `app/profanity_word_list.txt`.
- El sistema soporta distintos niveles de censura por sesión (`low`, `medium`, `high`).
- Puedes cambiar la base de datos modificando `DATABASE_URL` en `.env`.

---
  
## 🐳 Ejecución con Docker

Puedes levantar la aplicación usando Docker y Docker Compose:

```bash
docker compose build
docker compose up -d
```

Esto expondrá la API en `http://localhost:8000`.
Documentación de la API en `http://localhost:8000/docs`.
  
Autor: Juan Camilo Palacio Alvarez
