from src.iam.domain import model as iam_models
from uuid import uuid4
from pwdlib import PasswordHash
import secrets


class TestUserModel:
    User = iam_models.User
    UserRole = iam_models.UserRole

    # Tests of the user domain model

    def get_salt(self):
        return secrets.token_bytes(32)

    def hash_pw(self, password: str, salt: bytes):
        Password_Hash = PasswordHash.recommended()
        return Password_Hash.hash(password, salt=salt)

    def test_can_create_user_with_password_hash(self, test_settings):
        pw_plain = test_settings.test.password

        salt = self.get_salt()

        user = self.User(
            name="name",
            email="email",
            organization_id=uuid4(),
            role=self.UserRole.SUBMITTER,
            password_hash=self.hash_pw(password=pw_plain, salt=salt),
            password_salt=salt,
        )

        assert self.hash_pw(password=pw_plain, salt=salt) == user.password_hash
