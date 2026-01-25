from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

import pytest

from src.expense_management.application import expense_exception
from src.expense_management.application.services import (
    ExpenseApplicationService,
)
from src.iam.application.services import AuthorizationService
from src.expense_management.domain import model as expense_model
from src.iam.domain import model as user_model
from src.expense_management.infrastructure.repository import FakeExpenseRepository
from src.iam.infrastructure.repository import FakeUserRepository


def fake_user_repo(users: list[user_model.User]):
    return FakeUserRepository(users)


def generate_user(
    id: UUID = None,
    role: str = "submitter",
    org_id: UUID = None,
):
    if id is None:
        id = uuid4()
    if org_id is None:
        org_id = uuid4()

    if role == "approver":
        user_role = user_model.UserRole.APPROVER
    else:
        user_role = user_model.UserRole.SUBMITTER

    return user_model.User(
        id=id,
        name="user",
        email="i@u.com",
        role=user_role,
        organization_id=org_id,
    )


def generate_expense(submitter_id: UUID = uuid4(), org_id: UUID = uuid4()):
    return expense_model.Expense(
        submitter_id=submitter_id,
        date=datetime(2025, 1, 1),
        title="my expense",
        amount=100,
        category=expense_model.ExpenseCategory.OFFICE_SUPPLIES,
        organization_id=org_id,
    )


class TestExpenseAuthPolicy:
    def test_approver_is_allowed_to_approve(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)
        approver = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(submitter.id, org_id)
        ex_auth_service = AuthorizationService(
            fake_user_repo(users=[submitter, approver])
        )

        assert ex_auth_service.can_approve_expense(
            submitter_id=submitter.id,
            approver_id=approver.id,
            organization_id=expense.organization_id,
        )

    def test_cannot_self_approve(self):
        org_id = uuid4()
        approver = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(approver.id, org_id)
        ex_auth_service = AuthorizationService(fake_user_repo(users=[approver]))
        assert not ex_auth_service.can_approve_expense(
            approver.id, approver.id, expense.organization_id
        )

    def test_cannot_approve_with_submitter_role(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)
        submitter2 = generate_user(org_id=org_id)
        ex_auth_service = AuthorizationService(
            fake_user_repo(users=[submitter, submitter2])
        )
        assert not ex_auth_service.can_approve_expense(
            submitter.id, submitter2.id, org_id
        )

    def test_cannot_approve_with_different_org(self):
        org_id = uuid4()
        submitter = generate_user(org_id=org_id)
        approver = generate_user(role="approver")

        expense = generate_expense(submitter.id, org_id)
        ex_auth_service = AuthorizationService(
            fake_user_repo(users=[submitter, approver])
        )
        assert not ex_auth_service.can_approve_expense(
            submitter.id, approver.id, expense.organization_id
        )

    def test_can_approve_expense_as_other_approver(self):
        org_id = uuid4()
        approver1 = generate_user(role="approver", org_id=org_id)
        approver2 = generate_user(role="approver", org_id=org_id)

        expense = generate_expense(approver1.id, org_id)
        ex_auth_service = AuthorizationService(
            fake_user_repo(users=[approver1, approver2])
        )
        assert ex_auth_service.can_approve_expense(
            expense.submitter_id, approver2.id, expense.organization_id
        )


class TestExpenseAppService:
    def get_FakeUserRepo(self, users: list[user_model.User]):
        return FakeUserRepository(users=users)

    def get_FakeExpenseRepo(
        self, expenses: Optional[list[expense_model.Expense]] = None
    ):
        return FakeExpenseRepository(expenses=expenses)

    def get_AuthService(self, user_repo):
        return AuthorizationService(user_repo=user_repo)

    def get_ExpenseApplicationService(self, expense_repo, expense_auth_service):
        return ExpenseApplicationService(
            auth_service=expense_auth_service, expense_repo=expense_repo
        )

    def test_can_create_expense(self):
        org_id1 = uuid4()
        submitter = generate_user(org_id=org_id1)

        user_repo = self.get_FakeUserRepo(
            [
                submitter,
            ]
        )
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )

        assert isinstance(
            expense_app.create_expense(
                submitter.id,
                "title",
                datetime.now(),
                100.10,
                "OFFICE_SUPPLIES",
                submitter.organization_id,
            ),
            expense_model.Expense,
        )

    def test_can_get_expense_as_submitter(self):
        submitter = generate_user()
        user_repo = self.get_FakeUserRepo([submitter])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expenses = expense_app.find_expenses_by_user(submitter.id)
        assert expense in expenses

    def test_can_get_expense_as_approver_of_same_org(self):
        submitter = generate_user()
        approver = generate_user(role="approver", org_id=submitter.organization_id)
        user_repo = self.get_FakeUserRepo([submitter, approver])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expenses = expense_app.get_expenses_for_user_organization(
            approver.id, approver.organization_id
        )
        assert expense in expenses

    def test_cannot_get_expense_as_approver_of_other_org(self):
        submitter = generate_user()
        approver = generate_user(role="approver")
        user_repo = self.get_FakeUserRepo([submitter, approver])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        with pytest.raises(expense_exception.NotPermitted):
            expense_app.get_expenses_for_user_organization(
                approver.id, submitter.organization_id
            )

    def test_cannot_get_not_mine_expense_as_submitter(self):
        submitter1 = generate_user()
        submitter2 = generate_user(org_id=submitter1.organization_id)
        user_repo = self.get_FakeUserRepo([submitter1, submitter2])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense1 = expense_app.create_expense(
            submitter1.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter1.organization_id,
        )
        expense2 = expense_app.create_expense(
            submitter2.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter2.organization_id,
        )

        expenses = expense_app.find_expenses_by_user(submitter2.id)
        assert expenses
        assert expense2 in expenses
        assert expense1 not in expenses

    def test_can_submit_expense(self):
        submitter = generate_user()

        user_repo = self.get_FakeUserRepo(
            [
                submitter,
            ]
        )
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )
        expense_app.submit_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

    def test_cannot_submit_not_mine_expense(self):
        submitter = generate_user()

        user_repo = self.get_FakeUserRepo(
            [
                submitter,
            ]
        )
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )
        with pytest.raises(expense_exception.InvalidSubmitter):
            expense_app.submit_expense(user_id=uuid4(), expense_id=expense.id)

        assert expense.state.name == "DRAFT"

    def test_can_withdraw_my_expense(self):
        submitter = generate_user()

        user_repo = self.get_FakeUserRepo(
            [
                submitter,
            ]
        )
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )
        expense_app.withdraw_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "WITHDRAWN"

    def test_can_approve_expense_as_approver_of_same_org(self):
        submitter = generate_user()
        approver = generate_user(role="approver", org_id=submitter.organization_id)
        user_repo = self.get_FakeUserRepo([submitter, approver])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expense_app.submit_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

        expense_app.approve_expense(user_id=approver.id, expense_id=expense.id)

        assert expense.state.name == "APPROVED"

    def test_cannot_approve_as_approver_of_other_org(self):
        submitter = generate_user()
        approver = generate_user(role="approver")
        user_repo = self.get_FakeUserRepo([submitter, approver])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expense_app.submit_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

        with pytest.raises(expense_exception.InvalidApprover):
            expense_app.approve_expense(user_id=approver.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

    def test_cannot_approve_as_submitter_of_same_org(self):
        submitter = generate_user()
        submitter2 = generate_user(org_id=submitter.organization_id)
        user_repo = self.get_FakeUserRepo([submitter, submitter2])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expense_app.submit_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

        with pytest.raises(expense_exception.InvalidApprover):
            expense_app.approve_expense(user_id=submitter2.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

    def test_can_revoke_as_approver(self):
        submitter = generate_user()
        approver = generate_user(role="approver", org_id=submitter.organization_id)
        user_repo = self.get_FakeUserRepo([submitter, approver])
        expense_repo = self.get_FakeExpenseRepo()
        expense_auth_service = self.get_AuthService(user_repo=user_repo)
        expense_app = self.get_ExpenseApplicationService(
            expense_repo=expense_repo, expense_auth_service=expense_auth_service
        )
        expense = expense_app.create_expense(
            submitter.id,
            "title",
            datetime.now(),
            100.10,
            "OFFICE_SUPPLIES",
            submitter.organization_id,
        )

        expense_app.submit_expense(user_id=submitter.id, expense_id=expense.id)

        assert expense.state.name == "SUBMITTED"

        expense_app.approve_expense(user_id=approver.id, expense_id=expense.id)

        assert expense.state.name == "APPROVED"

        expense_app.revoke_approval(
            user_id=approver.id, expense_id=expense.id, reason="I have my reason"
        )

        assert expense.state.name == "REVOKED"
