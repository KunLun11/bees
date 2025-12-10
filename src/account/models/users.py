from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.account.models.base import AuditBase


class User(AuditBase):
    __tablename__ = "user_account"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
