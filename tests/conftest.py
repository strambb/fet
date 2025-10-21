import pytest
from uuid import UUID

from typing import Optional

import src.domain.repositories as repositories
import src.application.services as services


class FakeUser:
    """Test double for User"""

    def __init__(self, id: UUID, role: str, organization_id: UUID):
        self.id = id
        self.role = role
        self.organization_id = organization_id


class FakeUserRepository(repositories.IUserRepository):
    def __init__(self, users: Optional[list[FakeUser]] = None):
        self._users = {user.id: user for user in users} if users else {}

    def has_role(self, user_id: UUID, role: str) -> bool:
        user = self._users.get(user_id, None)
        return user.role == role if user else False

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool:
        user = self._users.get(user_id, None)
        return user.organization_id == org_id if user else False

    def exists(self, user_id):
        return user_id in self._users


@pytest.fixture
def getFakeUserRepository():
    return FakeUserRepository()


@pytest.fixture
def getExpenseAuthorizationService():
    return services.ExpenseAuthorizationService(FakeUserRepository)
