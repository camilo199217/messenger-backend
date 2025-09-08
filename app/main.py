from contextlib import asynccontextmanager
import os
from better_profanity import profanity
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.dependencies import get_session_service
from app.schemas.session import SessionFilters
from app.settings import get_settings
from app.core.db import init_db
from app.routers import auth, message, session as session_router, user, websocket


settings = get_settings()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BADWORDS_PATH = os.path.join(BASE_DIR, "profanity_word_list.txt")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    profanity.load_censor_words_from_file(BADWORDS_PATH)

    async for service in get_session_service():
        sessions = await service.session_list(params=SessionFilters(page=1, size=0))

        for s in sessions["items"]:
            service.manager.create_session(session=s)

    yield


app = FastAPI(
    lifespan=lifespan,
    title="API Messenger",
    description="Backend de mensajería con filtro",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_detail = exc.errors()[0] if exc.errors() else {}
    loc = error_detail.get("loc", [])
    field = loc[-1] if loc else ""
    msg = error_detail.get("msg", "Formato de mensaje inválido")
    # Mensaje personalizado para el campo 'sender'
    if field == "sender":
        details = "El campo 'sender' debe ser 'user' o 'system'"
    else:
        details = msg
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": {
                "code": "INVALID_FORMAT",
                "message": "Formato de mensaje inválido",
                "details": details,
            },
        },
    )


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Manejar exceptions de SlowAPI
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(message.router)
app.include_router(session_router.router)
app.include_router(user.router)
app.include_router(websocket.router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
