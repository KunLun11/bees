from datetime import timedelta
from typing import Any, Optional

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token


from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import config

from sqlalchemy.ext.asyncio import async_sessionmaker


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> Optional[Any]:
    try:
        user_id = int(token.sub)
        app = connection.app

        if not hasattr(app.state, "sessionmaker"):
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(config.database.url)
            sessionmaker = async_sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )
            app.state.sessionmaker = sessionmaker
        else:
            sessionmaker = app.state.sessionmaker

        async with sessionmaker() as db_session:
            from src.account.services import UserService

            user_service = UserService(session=db_session)
            user = await user_service.get_by_id(user_id)

            return user
    except Exception as e:
        print(f"Error retrieving user from token: {e}")
        return None


async def revoked_token_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> bool:
    return False


jwt_auth = JWTAuth[Any, Token](
    token_secret=config.auth.jwt_secret,
    retrieve_user_handler=retrieve_user_handler,
    revoked_token_handler=revoked_token_handler,
    algorithm=config.auth.jwt_algorithm,
    auth_header="Authorization",
    default_token_expiration=timedelta(minutes=config.auth.access_token_expire_minutes),
    exclude=[
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/schema",
        "/docs",
        "/redoc",
    ],
    exclude_http_methods=["OPTIONS"],
    scopes=["http"],
)
