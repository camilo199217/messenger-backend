import uuid
import jwt
from datetime import datetime, timedelta
from app.settings import get_settings

settings = get_settings()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration)
    to_encode.update(
        {"exp": expire, "jti": str(uuid.uuid4())}  # identificador único del token
    )
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt
