from dataclasses import dataclass, field
from enum import Enum, auto
from uuid import UUID, uuid4
from typing import Optional


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
    password_salt: Optional[str | bytes] = None
