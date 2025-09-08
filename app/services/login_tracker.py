from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.settings import Settings
from app.models.login_attempt import LoginAttempt


def is_blocked(*, username: str, ip: str, settings: Settings, session: Session) -> bool:
    """Verifica si un usuario está bloqueado por demasiados intentos fallidos de inicio de sesión."""
    if not settings.LOGIN_ATTEMPTS_ENABLED:
        return False  # Si el seguimiento de intentos de inicio de sesión está deshabilitado

    # 🗂️ Consulta para obtener los intentos de inicio de sesión del usuario
    stmt = (
        select(LoginAttempt)
        .where(LoginAttempt.username == username, LoginAttempt.ip_address == ip)
        .order_by(LoginAttempt.timestamp.desc())
    )

    attempts = session.exec(stmt).all()

    # 🔍 Encuentra las fallas consecutivas más recientes
    consecutive_failures = 0
    for attempt in attempts:
        if attempt.success:
            break  # se rompe la cadena al encontrar un login exitoso
        consecutive_failures += 1

    if consecutive_failures < settings.LOGIN_ATTEMPTS_MAX:
        return False

    # ⏳ Cálculo de tiempo de bloqueo exponencial
    last_attempt_time = attempts[0].timestamp
    block_duration = 2 ** (
        consecutive_failures - settings.LOGIN_ATTEMPTS_MAX
    )  # en minutos

    unblock_time = last_attempt_time + timedelta(minutes=block_duration)
    return datetime.utcnow() < unblock_time


def register_login_attempt(
    username: str, ip: str, success: bool, settings: Settings, session: Session
):
    """Registrar un intento de inicio de sesión."""
    if not settings.LOGIN_ATTEMPTS_ENABLED:
        return  # Si el seguimiento de intentos de inicio de sesión está deshabilitado

    # 📝 Registrar el intento de inicio de sesión
    attempt = LoginAttempt(username=username, ip_address=ip, success=success)
    session.add(attempt)
    session.commit()
