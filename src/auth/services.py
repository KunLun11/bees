from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.models.users import User
from src.account.services import UserService
from src.core.config import config


class TokenService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.secret = config.auth.jwt_secret
        self.algorithm = config.auth.jwt_algorithm

    def create_access_token(
        self,
        user_id: int,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=config.auth.access_token_expire_minutes
            )

        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: int,
        email: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=config.auth.refresh_token_expire_days
            )

        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                options={"verify_exp": True},
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        from src.utils.password import verify_password

        user = await self.user_service.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def refresh_access_token(self, refresh_token: str) -> Optional[dict]:
        try:
            payload = self.verify_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            user_id = int(payload["sub"])
            email = payload["email"]

            user = await self.user_service.get_by_id(user_id)
            if not user:
                return None

            new_access_token = self.create_access_token(user_id, email)

            return {
                "access_token": new_access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user_id": user_id,
                "email": email,
            }
        except (ValueError, KeyError, jwt.PyJWTError):
            return None


async def provide_token_service(
    db_session: AsyncSession,
) -> TokenService:
    from src.account.services import provide_user_service

    user_service = await provide_user_service(db_session)
    return TokenService(user_service)
