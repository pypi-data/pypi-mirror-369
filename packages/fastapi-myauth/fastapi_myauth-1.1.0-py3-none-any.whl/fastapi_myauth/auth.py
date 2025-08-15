from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from fastapi import APIRouter
from sqlmodel import Relationship, Session

from . import crud, models
from .api.deps import APIDependencies

UserT = TypeVar("UserT", bound=models.User)
UserReadT = TypeVar("UserReadT", bound=models.UserRead)
UserCreateT = TypeVar("UserCreateT", bound=models.UserCreate)
UserUpdateT = TypeVar("UserUpdateT", bound=models.UserUpdate)


@dataclass
class FastAuth(Generic[UserT, UserReadT, UserCreateT, UserUpdateT]):
    """
    FastAPI Authentication class.
    """

    get_db: Callable[[], Generator[Session, Any]]
    user_model: type[UserT]
    user_read: type[UserReadT]
    user_create: type[UserCreateT]
    user_update: type[UserUpdateT]

    def __post_init__(self):
        class User(self.user_model, table=True):
            refresh_tokens: list[models.RefreshToken] = Relationship(
                back_populates="authenticates", cascade_delete=True
            )

        self._internal_user_model = User

    @property
    def User(self) -> type[UserT]:
        """Returns the fully configured internal user model."""
        return self._internal_user_model  # type: ignore

    def crud_user(self) -> crud.CRUDUser[UserT, UserCreateT, UserUpdateT]:
        """
        Returns an instance of the user CRUD handler.
        """

        class CrudUser(crud.CRUDUser[self.User, self.user_create, self.user_update]):
            pass

        return CrudUser(self.User)

    def deps(self) -> APIDependencies:
        """
        Returns the dependency injection container for FastAPI Authentication.
        """
        return APIDependencies(
            crud_user=self.crud_user(),
            get_db=self.get_db,
        )

    def get_router(self) -> APIRouter:
        """
        Constructs and returns a pre-configured APIRouter with all auth routes.
        """
        from fastapi_myauth.api.v1 import get_login_router, get_user_router

        api_router = APIRouter()
        deps_instance = self.deps()

        api_router.include_router(
            get_user_router(
                crud_user=self.crud_user(),
                deps=deps_instance,
                user_model=self.User,
                user_read=self.user_read,
                user_create=self.user_create,
                user_update=self.user_update,
            ),
            prefix="/users",
            tags=["users"],
        )
        api_router.include_router(
            get_login_router(
                crud_user=self.crud_user(),
                deps=deps_instance,
                user_model=self.User,
                user_read=self.user_read,
                user_create=self.user_create,
                user_update=self.user_update,
            ),
            prefix="/login",
            tags=["login"],
        )

        return api_router
