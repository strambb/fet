from uuid import uuid4

from src._shared.infrastructure import orm
from src.iam.application.services import PasswordService
from src.iam.domain import model as user_model


def test_app_alive(testclient):
    response = testclient.get("/healthz")
    assert response.status_code == 200


class TestUserAPI:
    def test_can_get_token(self, postgres_session, testclient):
        org_id = uuid4()
        postgres_session.add(orm.OrganizationORM(id=org_id, name="test-org"))

        email = f"user-{uuid4()}@example.com"
        password = "Testpass1!"
        postgres_session.add(
            orm.UserORM(
                id=uuid4(),
                name="test",
                email=email,
                role=user_model.UserRole.SUBMITTER,
                organization_id=org_id,
                password_hash=PasswordService().generate_hash(password),
            )
        )
        postgres_session.commit()

        response = testclient.post(
            "/token",
            data={"username": email, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_user_is_admin(self, postgres_session, testclient):
        org_id = uuid4()
        postgres_session.add(orm.OrganizationORM(id=org_id, name="test-org"))

        email = f"user-{uuid4()}@example.com"
        password = "Testpass1!"
        postgres_session.add(
            orm.UserORM(
                id=uuid4(),
                name="test",
                email=email,
                role=user_model.UserRole.ADMIN,
                organization_id=org_id,
                password_hash=PasswordService().generate_hash(password),
            )
        )
        postgres_session.commit()

        response = testclient.post(
            "/token",
            data={"username": email, "password": password},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        token = response.json()["access_token"]
        assert token is not None

        testclient.headers = {"Authorization": f"Bearer {token}"}

        response = testclient.get("/users/me")
        assert (
            response.json()["role"] == "ADMIN"
        )  # TODO: Change which mapper to appropriate string

    def test_user_is_approver(self):
        raise NotImplementedError

    def test_user_is_authenticated(self):
        raise NotImplementedError

    def test_user_has_org(self):
        raise NotImplementedError

    def test_if_authenticated_admin_can_register_new_user(self):
        raise NotImplementedError


class TestExpenseAPI:
    def test_can_create_expense(self):
        raise NotImplementedError

    def test_can_submit_expense(self):
        raise NotImplementedError

    def test_can_get_my_expenses(self):
        raise NotImplementedError

    def test_can_approve_expense(self):
        raise NotImplementedError

    def test_can_reject_expense(self):
        raise NotImplementedError

    def test_can_update_expense(self):
        raise NotImplementedError

    def test_can_delete_expense(self):
        raise NotImplementedError

    def test_can_get_expense_by_id(
        self, add_fake_org, add_fake_user, add_fake_expense, testclient
    ):
        org = add_fake_org(name="fake_org")
        submitter = add_fake_user(org_id=org["id"])
        expense = add_fake_expense(
            submitter_id=submitter["id"], organization_id=org["id"]
        )
        token = None
        response = testclient.get(expense)

    def test_can_get_expenses_by_status(self):
        raise NotImplementedError

    def test_can_get_pending_expenses(self):
        raise NotImplementedError

    def test_can_get_approved_expenses(self):
        raise NotImplementedError

    def test_can_get_rejected_expenses(self):
        raise NotImplementedError

    def test_cannot_approve_own_expense(self):
        raise NotImplementedError

    def test_cannot_submit_without_required_fields(self):
        raise NotImplementedError

    def test_cannot_approve_without_permission(self):
        raise NotImplementedError

    def test_cannot_update_submitted_expense(self):
        raise NotImplementedError

    def test_cannot_delete_approved_expense(self):
        raise NotImplementedError
