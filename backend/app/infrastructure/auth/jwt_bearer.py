import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings


class JWTBearer(HTTPBearer):
    def __init__(self) -> None:
        super().__init__(auto_error=True)

    async def __call__(self, request: Request) -> str:  # type: ignore[override]
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)  # type: ignore[assignment]
        token = credentials.credentials
        return self._decode_token(token)

    def _decode_token(self, token: str) -> str:
        settings = get_settings()
        try:
            payload = jwt.decode(  # type: ignore[reportUnknownMemberType]
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        except jwt.ExpiredSignatureError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
            ) from err
        except jwt.InvalidTokenError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            ) from err

        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject.",
            )
        return user_id


jwt_bearer = JWTBearer()
