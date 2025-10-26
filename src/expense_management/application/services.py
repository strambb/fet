from src.expense_management.domain.repository import IExpenseRepository
from src.iam.domain.repository import IUserRepository
from src.expense_management.domain import model as expense_model
from src.expense_management.domain import exception as domain_expense
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.expense_management.application import expense_exception


class ExpenseAuthorizationService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def can_approve(self, expense: expense_model.Expense, approver_id: UUID) -> bool:
        """Checks if user can approve given expense"""
        if expense.submitter_id == approver_id:
            return False

        if not self._user_repo.has_role(approver_id, "APPROVER"):
            return False

        return self._user_repo.is_same_organization(
            approver_id, expense.organization_id
        )

    def can_submit(self, user_id: UUID):
        return self._user_repo.has_role(
            user_id, "SUBMITTER"
        ) | self._user_repo.has_role(user_id, "APPROVER")

    def is_approver(self, user_id: UUID) -> bool:
        return self._user_repo.has_role(user_id, "APPROVER")


class ExpenseApplicationService:
    def __init__(
        self,
        expense_auth_service: ExpenseAuthorizationService,
        expense_repo: IExpenseRepository,
    ):
        self._expense_auth = expense_auth_service
        self._expense_repo = expense_repo

    def create_expense(
        self,
        submitter_id: UUID,
        title: str,
        date: datetime,
        amount: float,
        category: str,
        organization_id: UUID,
        notes: Optional[str] = None,
        document_reference: Optional[str] = None,
    ) -> expense_model.Expense:
        # Build expense domain model

        expense = expense_model.Expense(
            submitter_id=submitter_id,
            title=title,
            date=date,
            amount=amount,
            category=expense_model.ExpenseCategory[category],
            organization_id=organization_id,
            notes=notes,
            document_reference=document_reference,
        )

        self._expense_repo.save(expense=expense)

        return expense

    def submit_expense(self, user_id: UUID, expense_id: UUID):
        expense = self._expense_repo.get(expense_id=expense_id)

        try:
            expense.submit(user_id)
        except domain_expense.InvalidSubmitUser:
            raise expense_exception.InvalidSubmitter

        # Persist
        self._expense_repo.save(expense)
        return expense

    def withdraw_expense(self, user_id: UUID, expense_id: UUID):
        expense = self._expense_repo.get(expense_id=expense_id)

        expense.withdraw(user_id)

        self._expense_repo.save(expense)
        return expense

    def approve_expense(self, user_id: UUID, expense_id: UUID):
        expense = self._expense_repo.get(expense_id=expense_id)

        # Check user can approve
        if not self._expense_auth.can_approve(expense, user_id):
            raise expense_exception.InvalidApprover

        expense.approve(user_id)

        self._expense_repo.save(expense)
        return expense

    def revoke_approval(self, user_id: UUID, expense_id: UUID, reason: str):
        expense = self._expense_repo.get(expense_id=expense_id)

        expense.revoke(by=user_id, reason=reason)

        self._expense_repo.save(expense=expense)
        return expense

    def get_related_expenses(self, user_id: UUID) -> list[expense_model.Expense]:
        return self._expense_repo.find_by_user(user_id)

    def get_all_org_expenses(
        self, user_id: UUID, org_id: UUID
    ) -> list[expense_model.Expense]:
        if not self._expense_auth.is_approver(
            user_id=user_id
        ) or not self._expense_auth._user_repo.is_same_organization(
            user_id=user_id, org_id=org_id
        ):
            raise expense_exception.NotPermitted("User is not permitted")

        return self._expense_repo.find_by_organization(org_id=org_id)
