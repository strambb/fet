from src.domain.repositories import IUserRepository
from src.domain.expense import model as expense_model
from uuid import UUID


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
            approver_id, expense.organization.id
        )

    def can_submit(self, user_id: UUID):
        return self._user_repo.has_role(
            user_id, "SUBMITTER"
        ) | self._user_repo.has_role(user_id, "APPROVER")
