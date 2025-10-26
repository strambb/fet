from dataclasses import dataclass, field
from uuid import uuid4, UUID


@dataclass(kw_only=True)
class Organization:
    name: str
    id: UUID = field(default_factory=uuid4)
