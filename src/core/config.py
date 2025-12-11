import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/bees_db"
    )
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class AuthConfig:
    jwt_secret: str = os.getenv(
        "JWT_SECRET", "muLQ23xSvVrOSuYkzOIFVAxjWOsUIn9zmRvYmVOBVUC"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    require_email_verification: bool = (
        os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
    )


@dataclass
class AppConfig:
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


@dataclass
class Config:
    database: DatabaseConfig
    auth: AuthConfig
    app: AppConfig

    def __init__(self):
        self.database = DatabaseConfig()
        self.auth = AuthConfig()
        self.app = AppConfig()


config = Config()
