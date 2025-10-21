import pytest
from uuid import uuid4
from tests.conftest import FakeUser





def test_approver_is_allowed_to_approve(expense_auth_service):
    expense_auth_service.can_approve()