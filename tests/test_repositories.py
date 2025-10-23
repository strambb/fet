from uuid import UUID, uuid4

from sqlalchemy import text

from src.domain.user import model as user_model
from src.infrastructure import orm
from src.infrastructure.repositories import (
    SqlAlchemyExpenseRepository,
    SqlAlchemyUserRepository,
)


def insert_org(session, commit: bool = False):
    org_id = uuid4()
    session.execute(
        text(f"INSERT INTO organizations (id, name) VALUES ('{org_id}', 'org1')")
    )
    [[organization_id]] = session.execute(
        text("SELECT id FROM organizations WHERE name=:org_name"), {"org_name": "org1"}
    )
    session.flush()
    if commit:
        session.commit()
    return org_id


def insert_submitter(session, org_id: UUID, commit: bool = False):
    user_id = uuid4()

    submitter = orm.UserORM(
        id=user_id,
        name="submitter",
        email="i@u.com",
        role=user_model.UserRole.SUBMITTER,
        organization_id=org_id,
    )
    session.add(submitter)
    session.flush()
    if commit:
        session.commit()
    return user_id


def insert_approver(session, org_id: UUID, commit: bool = False):
    user_id = uuid4()

    submitter = orm.UserORM(
        id=user_id,
        name="approver",
        email="q@u.com",
        role=user_model.UserRole.APPROVER,
        organization_id=org_id,
    )
    session.add(submitter)
    session.flush()
    if commit:
        session.commit()
    return user_id


class TestUserRepo:
    def test_can_check_organization_is_same(self, session):
        org_id = insert_org(session)
        submitter_id = insert_submitter(session, org_id=org_id)
        approver_id = insert_approver(session, org_id=org_id)

        approver = session.get(orm.UserORM, approver_id)

        user_repo = SqlAlchemyUserRepository(session)

        assert user_repo.is_same_organization(submitter_id, org_id)
        assert user_repo.is_same_organization(submitter_id, approver.organization_id)
        assert not user_repo.is_same_organization(submitter_id, uuid4())

    def test_can_check_user_roles(
        self,
        session,
    ):
        org_id = insert_org(session)
        submitter_id = insert_submitter(session, org_id=org_id)
        approver_id = insert_approver(session, org_id=org_id)

        user_repo = SqlAlchemyUserRepository(session)

        assert user_repo.has_role(submitter_id, "SUBMITTER")
        assert user_repo.has_role(approver_id, "APPROVER")
        assert not user_repo.has_role(submitter_id, "APPROVER")

    def test_can_check_existstance(self, session):
        org_id = insert_org(session)
        submitter_id = insert_submitter(session, org_id=org_id)

        user_repo = SqlAlchemyUserRepository(session)

        assert user_repo.exists(submitter_id)
        assert not user_repo.exists(uuid4())


class TestPersistantUserRepo:
    def test_can_load_persistant_repo(self, postgres_session):
        org_id = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id, commit=True)

        user_repo = SqlAlchemyUserRepository(postgres_session)

        assert user_repo.exists(submitter_id)
        assert not user_repo.exists(uuid4())
