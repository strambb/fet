import pytest
from uuid import uuid4, UUID
from src.application.services import ExpenseAuthorizationService
from src.domain.user import model as user_model
from src.domain.expense import model as expense_model
from src.infrastructure.repositories import FakeUserRepository
from datetime import datetime


def fake_user_repo(users: list[user_model.User]):
    return FakeUserRepository(users)


def generate_user(
    role: str = "submitter",
    org_id: UUID = uuid4(),
):
    if role == "approver":
        user_role = user_model.UserRole.APPROVER
    else:
        user_role = user_model.UserRole.SUBMITTER

    return user_model.User(
        name="user",
        email="i@u.com",
        role=user_role,
        organization_id=org_id,
    )


def generate_expense(submitter_id: UUID = uuid4(), org_id: UUID = uuid4()):
    return expense_model.Expense(
        submitter_id=str(submitter_id),
        date=datetime(2025, 1, 1),
        title="my expense",
        amount=100,
        category=expense_model.ExpenseCategory.OFFICE_SUPPLIES,
        organization=expense_model.Organization(id=org_id, name="my_org"),
    )


def test_approver_is_allowed_to_approve():
    org_id = uuid4()
    submitter = generate_user(org_id=org_id)
    approver = generate_user(role="approver", org_id=org_id)

    expense = generate_expense(submitter.id, org_id)
    ex_auth_service = ExpenseAuthorizationService(
        fake_user_repo(users=[submitter, approver])
    )

    assert ex_auth_service.can_approve(expense, approver.id)


def test_cannot_self_approve():
    org_id = uuid4()
    approver = generate_user(role="approver", org_id=org_id)

    expense = generate_expense(approver.id, org_id)
    ex_auth_service = ExpenseAuthorizationService(fake_user_repo(users=[approver]))
    assert not ex_auth_service.can_approve(expense, approver.id)


def test_cannot_approve_with_submitter_role():
    org_id = uuid4()
    submitter = generate_user(org_id=org_id)

    expense = generate_expense(submitter.id, org_id)
    ex_auth_service = ExpenseAuthorizationService(fake_user_repo(users=[submitter]))
    assert not ex_auth_service.can_approve(expense, submitter.id)


def test_cannot_approve_with_different_org():
    org_id = uuid4()
    submitter = generate_user(org_id=org_id)
    approver = generate_user(role="approver")

    expense = generate_expense(submitter.id, org_id)
    ex_auth_service = ExpenseAuthorizationService(
        fake_user_repo(users=[submitter, approver])
    )
    assert not ex_auth_service.can_approve(expense, approver.id)

def test_can_approve_as_other_approver():
    org_id = uuid4()
    approver1 = generate_user(role="approver", org_id=org_id)
    approver2 = generate_user(role="approver", org_id=org_id)

    expense = generate_expense(approver1.id, org_id)
    ex_auth_service = ExpenseAuthorizationService(fake_user_repo(users=[approver1, approver2]))
    assert ex_auth_service.can_approve(expense, approver2.id)