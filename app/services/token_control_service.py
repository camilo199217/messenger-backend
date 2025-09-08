import jwt
from sqlmodel import select
from app.models.revoked_token import RevokedToken
from app.settings import get_settings
from sqlmodel.ext.asyncio.session import AsyncSession

settings = get_settings()


class TokenControlService:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def revoke_token(self, *, token: str):
        try:
            payload = jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
            )
            jti = payload.get("jti")
            if jti:
                revoked = RevokedToken(jti=jti)
                await self.session.add(revoked)
                await self.session.commit()
        except jwt.JWTError:
            pass

    async def is_token_revoked(self, *, jti: str) -> bool:
        if jti:
            stmt = select(RevokedToken).where(RevokedToken.jti == jti)
            result = await self.session.exec(stmt)
            revoked_token = result.one_or_none()
            return revoked_token is not None
        return True  # si no hay jti, lo tratamos como inválido
