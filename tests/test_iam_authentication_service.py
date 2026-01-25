from src.iam.application.services import AuthenticationService
from src.iam.infrastructure.repository import FakeUserRepository


class TestAuthenticationService:
    def test_service_exists(self):
        assert AuthenticationService

    def test_service_has_user_repo(self):
        auth_service = AuthenticationService(user_repo=FakeUserRepository())
        assert auth_service.user_repo
