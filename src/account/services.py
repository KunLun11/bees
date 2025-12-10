import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.models.users import User
from src.account.schemas import UserCreate, UserUpdate
from src.utils.password import hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate):
        if await self.get_by_email(user_data.email):
            raise ValueError(f"User with email {user_data.email} already exists")  # noqa: EM102

        if await self.get_by_username(user_data.username):
            raise ValueError(f"User with username {user_data.username} already exists")  # noqa: EM102

        password_hash = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
        )
        self.session.add(user)
        try:
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Database error: {str(e)}")  # noqa: B904, EM102

    async def update(self, user_id: str, user_data: UserUpdate) -> User | None:
        user = await self.get_by_id(user_id)
        if not user:
            return None
        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.session.delete(user)
        await self.session.commit()
        return True


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)
