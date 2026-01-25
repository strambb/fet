import secrets
from uuid import UUID

from pwdlib import PasswordHash

from src.expense_management.application.services import ExpenseAuthorizationContract
from src.iam.domain.model import User, UserRole
from src.iam.domain.repository import IUserRepository
from src.iam.infrastructure import exception as iam_repo_exception
from src.iam.application import exception as iam_application_exception
import re
from typing import Protocol
from email_validator import validate_email, EmailNotValidError


class IPasswordService(Protocol):
    def generate_hash(self, plain_pw: str) -> str: ...
    def verify_password(
        self, plain_password: str, hash: str
    ) -> tuple[bool, (str | None)]: ...


class PasswordService:
    def __init__(self):
        self._hasher = PasswordHash.recommended()

    def generate_hash(self, plain_pw: str) -> str:
        return self._hasher.hash(plain_pw)

    def verify_password(
        self, plain_password: str, hash: str
    ) -> tuple[bool, (str | None)]:
        return self._hasher.verify_and_update(password=plain_password, hash=hash)


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


class AuthenticationService:
    # Contract to be defined with API? Where?

    def __init__(self, user_repo: IUserRepository, password_service: IPasswordService):
        self.user_repo = user_repo
        self.password_service = password_service

    def _validate_password(self, password) -> None:
        """
        Validate password based on following rules:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        - Al least 8 characters
        - Maximum 128 characters

        :param password: password to be validated
        """

        if len(password) < 8:
            raise iam_application_exception.InsecurePassword(
                "Password must be at least 8 characters long."
            )

        if len(password) > 128:
            raise iam_application_exception.InsecurePassword(
                "Password too long. Maximum 128 characters."
            )

        if not re.search(r"[a-z]", password):
            raise iam_application_exception.InsecurePassword(
                "Password must contain lowercase letter."
            )

        if not re.search(r"[A-Z]", password):
            raise iam_application_exception.InsecurePassword(
                "Password must contain uppercase letter."
            )

        if not re.search(r"\d", password):
            raise iam_application_exception.InsecurePassword(
                "Password must contain at least one digit."
            )

        if not re.search(r"[!@#$%^&*(),.?:{}|<>]", password):
            raise iam_application_exception.InsecurePassword(
                "Password must contain at least one special character of [!@#$%^&*(),.?:{}|<>]."
            )

    def _validate_and_normalize_email(self, email: str) -> str:
        try:
            email_info = validate_email(email, check_deliverability=False)
            email = email_info.normalized
            return email

        except EmailNotValidError as e:
            raise iam_application_exception.InvalidEmail(f"Email not valid: {e}")

    def register_user(self, name: str, email: str, password: str, org_id: UUID) -> User:
        
        email = self._validate_and_normalize_email(email=email)
        self._validate_password(password=password)

        if self.user_repo.exists_by_email(email):
            raise iam_application_exception.DuplicateEmail(
                f"Email {email} is already registered"
            )

        user = User(
            name=name,
            email=email,
            role=UserRole.SUBMITTER,  # Default role is submitter
            organization_id=org_id,
            password_hash=self.password_service.generate_hash(plain_pw=password),
        )
        try:
            self.user_repo.save(user)

        except iam_repo_exception.UserTranslationError as e:
            raise iam_application_exception.UserRegistrationError(
                f"Failed to create user: {e}"
            ) from e
        except Exception as e:
            # logger.error...
            raise iam_application_exception.UserRegistrationError(
                f"An unexpected error occurred during registration: {e}"
            )

        return user
