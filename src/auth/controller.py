import logging
from datetime import timedelta

from litestar import Controller, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from src.auth.jwt_auth import jwt_auth
from src.core.config import config
from src.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from src.auth.services import TokenService, provide_token_service
from src.account.services import UserService, provide_user_service
from src.account.schemas import UserCreate

logger = logging.getLogger(__name__)


class AuthController(Controller):
    tags = ["Authentication"]
    path = "/auth"
    dependencies = {
        "token_service": Provide(provide_token_service),
        "user_service": Provide(provide_user_service),
    }

    @post("/login")
    async def login(
        self,
        token_service: TokenService,
        user_service: UserService,
        data: LoginRequest,
    ) -> LoginResponse:
        try:
            user = await token_service.authenticate_user(data.email, data.password)
            if not user:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                )
            access_token = jwt_auth.create_token(
                identifier=str(user.id),
                token_expiration=timedelta(
                    minutes=config.auth.access_token_expire_minutes
                ),
                token_extras={"email": user.email, "type": "access"},
            )
            refresh_token = token_service.create_refresh_token(user.id, user.email)

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                email=user.email,
            )

        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )

    @post("/register", status_code=HTTP_201_CREATED)
    async def register(
        self,
        user_service: UserService,
        token_service: TokenService,
        data: RegisterRequest,
    ) -> LoginResponse:
        try:
            user_create = UserCreate(
                email=data.email,
                username=data.username or data.email.split("@")[0],
                password=data.password,
            )

            user = await user_service.create(user_create)
            access_token = jwt_auth.create_token(
                identifier=str(user.id),
                token_expiration=timedelta(
                    minutes=config.auth.access_token_expire_minutes
                ),
                token_extras={"email": user.email, "type": "access"},
            )

            refresh_token = token_service.create_refresh_token(user.id, user.email)

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                email=user.email,
            )

        except ValueError as e:
            logger.error(f"Registration error: {e}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected registration error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Registration failed",
            )

    @post("/refresh")
    async def refresh_token(
        self,
        token_service: TokenService,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        try:
            result = await token_service.refresh_access_token(data.refresh_token)
            if not result:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
            return TokenResponse(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                token_type=result["token_type"],
            )

        except Exception as e:
            logger.error(f"Token refresh error: {e}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed",
            )

    @post("/logout")
    async def logout(self) -> dict:
        return {"message": "Successfully logged out"}
