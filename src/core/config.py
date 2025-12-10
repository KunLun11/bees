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


# @dataclass
# class OAuthConfig:
#     google_client_id: str = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
#     google_client_secret: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
#     google_redirect_uri: str = os.getenv(
#         "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
#     )

#     github_client_id: str = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")
#     github_client_secret: str = os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "")
#     github_redirect_uri: str = os.getenv(
#         "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"
#     )

#     cookie_name: str = "oauth_state"
#     cookie_secure: bool = os.getenv("OAUTH_COOKIE_SECURE", "false").lower() == "true"
#     state_expiration: int = int(os.getenv("OAUTH_STATE_EXPIRATION", "600"))


@dataclass
class AppConfig:
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))


class Config:
    def __init__(self):
        self.database = DatabaseConfig()
        self.auth = AuthConfig()
        self.app = AppConfig()


config = Config()
