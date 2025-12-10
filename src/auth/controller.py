import logging

from litestar import Controller, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from src.account.schemas import UserCreate
from src.account.services import UserService, provide_user_service
from src.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from src.auth.service import AuthService

logger = logging.getLogger(__name__)


async def provide_auth_service() -> AuthService:
    return AuthService()


class AuthController(Controller):
    path = "/auth"
    dependencies = {
        "user_service": Provide(provide_user_service),
        "auth_service": Provide(provide_auth_service),
    }

    @post("/register", status_code=HTTP_201_CREATED)
    async def register(
        self,
        user_service: UserService,
        data: RegisterRequest,
    ) -> dict:
        try:
            user_create = UserCreate(
                email=data.email,
                username=data.username,
                password=data.password,
            )
            user = await user_service.create(user_create)
            return {
                "message": "User registered successfully",
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
            }
        except ValueError as e:
            if "already exists" in str(e).lower():
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))  # noqa: B904
            raise HTTPException(  # noqa: B904
                status_code=HTTP_400_BAD_REQUEST, detail=f"Validation error: {str(e)}"
            )

    @post("/login")
    async def login(
        self, user_service: UserService, auth_service: AuthService, data: LoginRequest
    ) -> LoginResponse:
        user = await auth_service.authenticate_user(
            user_service,
            data.email,
            data.password,
        )
        if not user:
            logger.warning(f"Failed login for email: {data.email}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
            )
        logger.info(f"Login successful for user: {user.id}")

        access_token = auth_service.create_access_token(user)
        refresh_token = auth_service.create_refresh_token(user)
        logger.debug(f"Tokens generated for user {user.id}")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
        )

    @post("/refresh")
    async def refresh(
        self,
        user_service: UserService,
        auth_service: AuthService,
        data: RefreshTokenRequest,
    ) -> TokenResponse:
        payload = auth_service.verify_token(data.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError):
            raise HTTPException(  # noqa: B904
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        new_access_token = auth_service.create_access_token(user)
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
        )

    @post("/logout")
    async def logout(self) -> dict:
        return {
            "message": "Successfully logged out. Please delete tokens on client side."
        }
