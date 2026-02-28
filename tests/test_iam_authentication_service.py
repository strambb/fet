from uuid import uuid4

import pytest
from random import choices
from string import ascii_letters

from src.iam.application import exception
from src.iam.application.services import AuthenticationService, PasswordService
from src.iam.infrastructure.repository import FakeUserRepository
from src.iam.domain.model import User, UserRole


class TestAuthenticationService:
    def test_service_exists(self):
        assert AuthenticationService

    def test_service_has_user_repo(self):
        pws = PasswordService()
        auth_service = AuthenticationService(
            user_repo=FakeUserRepository(), password_service=pws
        )
        assert auth_service.user_repo

    def test_given_good_password_and_email_then_can_register_user(self, test_settings):
        pws = PasswordService()
        auth_service = AuthenticationService(
            user_repo=FakeUserRepository(), password_service=pws
        )

        org_id = uuid4()

        user = auth_service.register_user(
            name="testuser",
            email="test@mgoebel.xyz",
            password=test_settings.test.password,
            org_id=org_id,
        )

        assert user == auth_service.user_repo.get(user.id)

    def test_given_bad_password_then_cannot_register_user(self):
        pws = PasswordService()
        auth_service = AuthenticationService(
            user_repo=FakeUserRepository(), password_service=pws
        )

        bad_passwords = [
            "short",
            "nouppercase123!",  # no uppercase
            "NOLOWERCASE123#",  # no lowercase
            "NoSpecialChar123",  # no special character
            "NoNumber#%",  # no number
            "A" * 129 + "a!1",  # to long
        ]

        org_id = uuid4()

        for bad_password in bad_passwords:
            with pytest.raises(exception.InsecurePassword) as e:
                _ = auth_service.register_user(
                    name="testuser",
                    email="test@mgoebel.xyz",
                    password=bad_password,
                    org_id=org_id,
                )
            assert "Password must " in str(e) or "Password too long" in str(e)

    def test_given_bad_email_then_cannot_register_user(self, test_settings):
        pws = PasswordService()
        auth_service = AuthenticationService(
            user_repo=FakeUserRepository(), password_service=pws
        )

        org_id = uuid4()

        bad_emails = ["i", "@d.de", "i.de", "@.de", "@.", "i@asd@.de"]

        for bad_email in bad_emails:
            with pytest.raises(exception.InvalidEmail) as e:
                _ = auth_service.register_user(
                    name="testuser",
                    email=bad_email,
                    password=test_settings.test.password,
                    org_id=org_id,
                )
            assert "Email not valid:" in str(e)

    def test_given_duplicate_email_then_cannot_register_user(self, test_settings):
        pws = PasswordService()
        auth_service = AuthenticationService(
            user_repo=FakeUserRepository(), password_service=pws
        )

        org_id = uuid4()
        _ = auth_service.register_user(
            name="testuser",
            email="test@mgoebel.xyz",
            password=test_settings.test.password,
            org_id=org_id,
        )

        with pytest.raises(exception.DuplicateEmail) as e:
            _ = auth_service.register_user(
                name="testuser",
                email="test@mgoebel.xyz",
                password=test_settings.test.password,
                org_id=org_id,
            )
        assert "already" in str(e)


class TestAuthentication:
    authn_service = AuthenticationService(
        user_repo=FakeUserRepository(), password_service=PasswordService()
    )

    def get_user(self, password: str, email: str | None = None):
        org_id = uuid4()
        user = self.authn_service.register_user(
            name="testuser",
            email=email
            if email
            else "".join(choices(ascii_letters, k=5)) + "@mgoebel.xyz",
            password=password,
            org_id=org_id,
        )

        return user, org_id

    def test_given_good_email_and_pw_user_is_authenticated(self, test_settings):
        fake_user, _ = self.get_user(test_settings.test.password)

        assert isinstance(
            self.authn_service.authenticate_user(
                email=fake_user.email, password=test_settings.test.password
            ),
            User,
        )

    def test_given_bad_email_good_pw_then_not_authenticated(self, test_settings):
        _ = self.get_user(test_settings.test.password)

        with pytest.raises(exception.InvalidEmail):
            _ = self.authn_service.authenticate_user(
                "1@u.de", test_settings.test.password
            )

    def test_given_good_email_bad_pw_then_not_authenticated(self, test_settings):
        fake_user, _ = self.get_user(password=test_settings.test.password)

        with pytest.raises(exception.InvalidPassword):
            _ = self.authn_service.authenticate_user(fake_user.email, "some")


class TestPasswordService:
    def test_service_exists(self):
        assert PasswordService

    def test_hash_password_and_verify(self):
        pws = PasswordService()

        hash = pws.generate_hash("some")

        assert "argon2id" in hash

        valid, _ = pws.verify_password("some", hash)

        assert valid
