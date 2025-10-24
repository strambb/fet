from src.domain.repositories import IUserRepository, IExpenseRepository
from src.domain.expense import model as expense_model
from uuid import UUID
from datetime import datetime
from typing import Optional


class ExpenseAuthorizationService:
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def can_approve(self, expense: expense_model.Expense, approver_id: UUID) -> bool:
        """Checks if user can approve given expense"""
        if expense.submitter_id == str(approver_id):
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
