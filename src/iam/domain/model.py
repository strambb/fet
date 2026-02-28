import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from uuid import UUID, uuid4

from src.iam.domain import exception as iam_domain_exception


class UserRole(Enum):
    SUBMITTER = auto()
    APPROVER = auto()
    ADMIN = auto()


@dataclass(kw_only=True)
class User:
    id: UUID = field(default_factory=uuid4)
    name: str
    email: str
    role: UserRole
    organization_id: UUID
    password_hash: Optional[str] = None


@dataclass
class Password:
    _value: str

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
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

        if len(self._value) < 8:
            raise iam_domain_exception.InsecurePassword(
                "Password must be at least 8 characters long."
            )

        if len(self._value) > 128:
            raise iam_domain_exception.InsecurePassword(
                "Password too long. Maximum 128 characters."
            )

        if not re.search(r"[a-z]", self._value):
            raise iam_domain_exception.InsecurePassword(
                "Password must contain lowercase letter."
            )

        if not re.search(r"[A-Z]", self._value):
            raise iam_domain_exception.InsecurePassword(
                "Password must contain uppercase letter."
            )

        if not re.search(r"\d", self._value):
            raise iam_domain_exception.InsecurePassword(
                "Password must contain at least one digit."
            )

        if not re.search(r"[!@#$%^&*(),.?:{}|<>]", self._value):
            raise iam_domain_exception.InsecurePassword(
                "Password must contain at least one special character of [!@#$%^&*(),.?:{}|<>]."
            )

    def __repr__(self):
        return "Password(***)"
