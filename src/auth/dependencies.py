from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.account.services import UserService


async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    from litestar import Request

    request: Request = Request
    sessionmaker = request.app.state.sessionmaker
    async with sessionmaker() as session:
        try:
            yield session
        finally:
            await session.close()


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)
