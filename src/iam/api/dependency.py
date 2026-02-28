## Dependencies like get current user
from fastapi import Depends
from src._shared.infrastructure.database import get_db_session
from src.iam.application.services import AuthenticationService, PasswordService
from src.iam.infrastructure.repository import SqlAlchemyUserRepository


def get_session():
    session = next(get_db_session())()
    return session


def get_user_repo(session=Depends(get_session)):
    return SqlAlchemyUserRepository(session=session)


def get_authn_service(user_repo=Depends(get_user_repo)):

    pws = PasswordService()
    return AuthenticationService(user_repo=user_repo, password_service=pws)
