from dataclasses import dataclass
from uuid import UUID, uuid4

from enum import Enum, auto


class UserRole(Enum):
    SUBMITTER = auto()
    APPROVER = auto()
    ADMIN = auto()


@dataclass(kw_only=True)
class User:
    id: UUID = uuid4()
    firstname: str
    lastname: str
    email: str
    role: UserRole
    organization_id: UUID
    role: UserRole
    organization_id: UUID
