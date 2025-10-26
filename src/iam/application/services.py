from src.expense_management.application.services import ExpenseAuthorizationContract
from src.iam.domain.repository import IUserRepository
from uuid import UUID


class AuthorizationService(ExpenseAuthorizationContract):
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def can_approve_expense(
        self, submitter_id: UUID, approver_id: UUID, organization_id: UUID
    ) -> bool:
        """Checks if user can approve given expense"""
        if submitter_id == approver_id:
            return False

        if not self._user_repo.has_role(approver_id, "APPROVER"):
            return False

        return self._user_repo.is_same_organization(approver_id, organization_id)

    def can_submit_expense(self, user_id: UUID):
        return self._user_repo.has_role(
            user_id, "SUBMITTER"
        ) | self._user_repo.has_role(user_id, "APPROVER")

    def is_approver(self, user_id: UUID) -> bool:
        return self._user_repo.has_role(user_id, "APPROVER")

    def is_same_organization(self, user_id: UUID, org_id: UUID):
        return self._user_repo.is_same_organization(user_id=user_id, org_id=org_id)
