from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from litestar.connection import ASGIConnection
from litestar.security.jwt import Token

from src.account.models.users import User
from src.account.services import UserService
from src.core.config import config
from src.utils.password import verify_password


class AuthService:
    def __init__(self):
        self.secret_key = config.auth.jwt_secret
        self.algorithm = config.auth.jwt_algorithm
        self.access_token_expire_minutes = config.auth.access_token_expire_minutes
        self.refresh_token_expire_days = 2

    async def authenticate_user(
        self,
        user_service: UserService,
        email: str,
        password: str,
    ) -> User | None:
        user = await user_service.get_by_email(email)
        if not user:
            return None
        if verify_password(password, user.password_hash):
            return user
        return None

    def create_access_token(self, user: User):
        expire = datetime.now(UTC) + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def create_refresh_token(self, user: User) -> str:
        expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "exp": expire,
            "type": "refresh",
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def verify_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.PyJWTError:
            return None

    async def retrieve_user_handler(
        self,
        token: Token,
        connection: ASGIConnection,
    ) -> User | None:
        user_service: UserService | None = connection.dependencies.get("user_service")
        if not user_service:
            user_service = connection.app.state.get("user_service")
            if not user_service:
                return None

        try:
            user_id = int(token.sub)
            return await user_service.get_by_id(user_id)
        except (ValueError, TypeError):
            return None
