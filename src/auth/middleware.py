from litestar.security.jwt import JWTAuth

from src.auth.service import AuthService
from src.core.config import config

auth_service = AuthService()

jwt_auth = JWTAuth[dict](
    retrieve_user_handler=auth_service.retrieve_user_handler,
    token_secret=config.auth.jwt_secret,
    algorithm=config.auth.jwt_algorithm,
    exclude=[
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/docs",
        "/schema",
        "/openapi.json",
    ],
)
