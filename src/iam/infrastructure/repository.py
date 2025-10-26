from uuid import UUID
from typing import Optional
from src.iam.infrastructure import exception
from src.iam.domain import repository
from src.iam.domain import model as user_model
from sqlalchemy.orm import Session
from src._shared.infrastructure import orm


### User repos
class SqlAlchemyUserRepository(repository.IUserRepository):
    def __init__(self, session: Session):
        self._session = session

    def has_role(self, user_id: UUID, role: str) -> bool:
        user_orm = self._session.get(orm.UserORM, user_id)
        return user_orm.role.name == role if user_orm else False

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool:
        user_orm = self._session.get(orm.UserORM, user_id)
        return user_orm.organization_id == org_id if user_orm else False

    def exists(self, user_id: UUID):
        return self._session.get(orm.UserORM, user_id) is not None

    def get(self, user_id: UUID):
        user = self._session.get(orm.UserORM, user_id)
        if not user:
            raise exception.UserNotFound
        return user.to_domain()


class FakeUserRepository(repository.IUserRepository):
    def __init__(self, users: Optional[list[user_model.User]] = None):
        self._users = {user.id: user for user in users} if users else {}

    def has_role(self, user_id: UUID, role: str) -> bool:
        user = self._users.get(user_id, None)
        return user.role.name == role if user else False

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool:
        user = self._users.get(user_id, None)
        return user.organization_id == org_id if user else False

    def exists(self, user_id):
        return user_id in self._users

    def get(self, user_id: UUID):
        user = self._users.get(user_id, None)
        if not user:
            raise exception.UserNotFound
        return user
