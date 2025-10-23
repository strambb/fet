import pytest
from uuid import uuid4, UUID
from src.application.services import ExpenseAuthorizationService
from src.domain.user import model as user_model
from src.domain.expense import model as expense_model
from src.infrastructure.repositories import FakeUserRepository, FakeExpenseRepository
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


class TestExpenseAuthService:
    def test_approver_is_allowed_to_approve(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)
        approver = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(submitter.id, org_id)
        ex_auth_service = ExpenseAuthorizationService(
            fake_user_repo(users=[submitter, approver])
        )

        assert ex_auth_service.can_approve(expense, approver.id)

    def test_cannot_self_approve(self):
        org_id = uuid4()
        approver = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(approver.id, org_id)
        ex_auth_service = ExpenseAuthorizationService(fake_user_repo(users=[approver]))
        assert not ex_auth_service.can_approve(expense, approver.id)

    def test_cannot_approve_with_submitter_role(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)

        expense = generate_expense(submitter.id, org_id)
        ex_auth_service = ExpenseAuthorizationService(fake_user_repo(users=[submitter]))
        assert not ex_auth_service.can_approve(expense, submitter.id)

    def test_cannot_approve_with_different_org(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)
        approver = generate_user(role="approver")

        expense = generate_expense(submitter.id, org_id)
        ex_auth_service = ExpenseAuthorizationService(
            fake_user_repo(users=[submitter, approver])
        )
        assert not ex_auth_service.can_approve(expense, approver.id)

    def test_can_approve_as_other_approver(self):
        org_id = uuid4()
        approver1 = generate_user(role="approver", org_id=org_id)
        approver2 = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(approver1.id, org_id)
        ex_auth_service = ExpenseAuthorizationService(
            fake_user_repo(users=[approver1, approver2])
        )
        assert ex_auth_service.can_approve(expense, approver2.id)


class TestExpenseAppService:
    def get_expense_app_service(self):
        # generate users and expenses to be added to the fake repos
        expense_repo = FakeExpenseRepository
        user = generate_user()
        user_repo = FakeUserRepository([user])

        expense_auth = ExpenseAuthorizationService(user_repo=user_repo)

    #     return ExpenseApplicationService(expense_auth)

    # def test_can_create_expense(self):
    #     expense_app = self.get_expense_app_service()

    #     expense_app.create_expense(
    #         user,
    #         "title",
    #         amount...
    #     )

    def test_can_get_expense_as_submitter(self):
        expense_app = self.get_expense_app_service()
        raise NotImplementedError

    def test_can_get_expense_as_approver_of_same_org(self):
        raise NotImplementedError

    def test_cannot_get_expense_as_approver_of_other_org(self):
        raise NotImplementedError

    def test_cannot_get_not_mine_expense_as_submitter(self):
        raise NotImplementedError

    def test_can_submit_expense(self):
        expense_app = self.get_expense_app_service()
        raise NotImplementedError

    def test_can_withdraw_my_expense(self):
        raise NotImplementedError

    def test_can_approve_as_approver_of_same_org(self):
        raise NotImplementedError

    def test_cannot_approve_as_approver_of_other_org(self):
        raise NotImplementedError

    def test_can_revoke_as_approver(self):
        raise NotImplementedError
