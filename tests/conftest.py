import pytest
from uuid import UUID, uuid4()

from typing import Optional

from src.domain.expense import model as expense_model

import src.application.services as services





@pytest.fixture
def fake_user_repository():
    return FakeUserRepository(
        users=[
            FakeUser(id=UUID("12345678-1111-5678-1234-567812345678"), role="MEMBER", organization_id=UUID("12345678-1234-5678-1234-567812345678")),
            FakeUser(id=UUID("12345678-2222-5678-1234-567812345678"), role="APPROVER", organization_id=UUID("12345678-1234-5678-1234-567812345678")),
            FakeUser(id=UUID("12345678-1111-2222-1234-567812345678"), role="ADMIN", organization_id=UUID("12345678-1234-5678-1234-567812345678")),
        ]
    )


