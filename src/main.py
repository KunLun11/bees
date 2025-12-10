import os
from dotenv import load_dotenv
from litestar import Litestar

from litestar.plugins.sqlalchemy import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)

from src.account.controller import UserController
from src.auth.controller import AuthController
from src.auth.middleware import jwt_auth


load_dotenv()

os.environ.setdefault("JWT_SECRET", "muLQ23xSvVrOSuYkzOIFVAxjWOsUIn9zmRvYmVOBVUC")
session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/bees_db"
    ),
    session_config=session_config,
)
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


app = Litestar(
    route_handlers=[UserController, AuthController],
    plugins=[sqlalchemy_plugin],
    middleware=[jwt_auth.middleware],
)
