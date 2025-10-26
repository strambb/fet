from src.expense_management.domain.repository import IExpenseRepository
from src.expense_management.domain import model as expense_model
from src.expense_management.domain import exception as domain_expense
from uuid import UUID
from datetime import datetime
from typing import Optional, Protocol
from src.expense_management.application import expense_exception


class ExpenseAuthorizationContract(Protocol):
    def can_approve_expense(
        self, submitter_id: UUID, approver_id: UUID, organization_id: UUID
    ) -> bool:
        """Checks if user can approve given expense"""
        ...

    def can_submit_expense(self, user_id: UUID) -> bool: ...

    def is_approver(self, user_id: UUID) -> bool: ...

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool: ...


class ExpenseApplicationService:
    def __init__(
        self,
        auth_service: ExpenseAuthorizationContract,
        expense_repo: IExpenseRepository,
    ):
        self._auth_service = auth_service
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
        if not self._auth_service.can_approve_expense(
            expense.submitter_id, user_id, expense.organization_id
        ):
            raise expense_exception.InvalidApprover

        expense.approve(user_id)

        self._expense_repo.save(expense)
        return expense

    def revoke_approval(self, user_id: UUID, expense_id: UUID, reason: str):
        expense = self._expense_repo.get(expense_id=expense_id)

        expense.revoke(by=user_id, reason=reason)

        self._expense_repo.save(expense=expense)
        return expense

    def find_expenses_by_user(self, user_id: UUID) -> list[expense_model.Expense]:
        return self._expense_repo.find_by_user(user_id)

    def get_expenses_for_user_organization(self, user_id: UUID, org_id: UUID):
        if not self._auth_service.is_approver(
            user_id=user_id
        ) or not self._auth_service.is_same_organization(user_id, org_id):
            raise expense_exception.NotPermitted("User is not permitted")

        return self._expense_repo.find_by_organization(org_id=org_id)
