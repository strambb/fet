from src.iam.domain import model as iam_models
from src.iam.domain import exception as iam_domain_exceptions
from uuid import uuid4
from pwdlib import PasswordHash
import secrets
import pytest


class TestUserModel:
    User = iam_models.User
    UserRole = iam_models.UserRole

    # Tests of the user domain model

    def hash_pw(self, password: str):
        Password_Hash = PasswordHash.recommended()
        return Password_Hash.hash(password)

    def test_can_create_user_with_password_hash(self, test_settings):
        pw_plain = test_settings.test.password

        user = self.User(
            name="name",
            email="email",
            organization_id=uuid4(),
            role=self.UserRole.SUBMITTER,
            password_hash=self.hash_pw(password=pw_plain),
        )

        assert user.password_hash
        assert PasswordHash.recommended().verify(
            password=pw_plain, hash=user.password_hash
        )

class TestPasswordModel:
    Password = iam_models.Password
    
    def test_given_good_password_then_get_repr(self, test_settings):
        pw = self.Password(test_settings.test.password)
        assert str(pw) == "Password(***)"
    
    def test_given_bad_pass_then_get_validation_error(self):
        bad_passwords = [
            "short",
            "nouppercase123!",  # no uppercase
            "NOLOWERCASE123#",  # no lowercase
            "NoSpecialChar123",  # no special character
            "NoNumber#%",  # no number
            "A" * 129 + "a!1",  # to long
        ]

        for bad_password in bad_passwords:
            with pytest.raises(iam_domain_exceptions.InsecurePassword) as e:
                _ = self.Password(bad_password)
            assert "Password must " in str(e) or "Password too long" in str(e)
    