import logging
from litestar import Controller, get, post, delete
from litestar.di import Provide
from litestar.status_codes import (
    HTTP_409_CONFLICT,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_204_NO_CONTENT,
)
from litestar.exceptions import HTTPException

from src.account.schemas import UserCreate, UserListResponse, UserResponse
from src.account.services import UserService, provide_user_service

from src.auth.middleware import jwt_auth

logger = logging.getLogger(__name__)


class UserController(Controller):
    path = "/users"
    dependencies = {"user_service": Provide(provide_user_service)}
    quards = [jwt_auth.guards]

    @get(path="/users")
    async def list_users(
        self,
        user_service: UserService,
    ) -> list[UserListResponse]:
        try:
            users = await user_service.get_all()
            return [UserListResponse.model_validate(user) for user in users]
        except Exception as e:
            logger.error(f"Error in list_users: {e}", exc_info=True)
            raise

    @post(path="/users", status_code=HTTP_201_CREATED)
    async def create_user(
        self,
        user_service: UserService,
        data: UserCreate,
    ) -> UserResponse:
        try:
            user = await user_service.create(data)
            return UserResponse.model_validate(user)
        except ValueError as e:
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=str(e))

    @get(path="/users/{user_id:int}")
    async def get_user(
        self,
        user_service: UserService,
        user_id: int,
    ) -> UserResponse:
        user = await user_service.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
            )
        return UserResponse.model_validate(user)

    @delete(path="/users/{user_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_user(
        self,
        user_service: UserService,
        user_id: int,
    ) -> None:
        if not await user_service.delete(user_id):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=f"User {user_id} not found"
            )
