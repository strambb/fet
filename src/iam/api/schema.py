from pydantic import BaseModel
from uuid import UUID


class TokenModel(BaseModel):
    access_token: str
    token_type: str


class TokenDataModel(BaseModel):
    email: str | None = None


class UserResponseModel(BaseModel):
    id: UUID 
    name: str
    email: str
    role: str
    organization_id: UUID

