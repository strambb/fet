from uuid import UUID, uuid4
from src.infrastructure.repositories import (
    SqlAlchemyExpenseRepository,
    SqlAlchemyUserRepository,
)
from src.infrastructure import orm
from src.domain.user import model as user_model
from sqlalchemy import text


def insert_org(session):
    org_id = uuid4()
    session.execute(
        text(f"INSERT INTO organizations (id, name) VALUES ('{org_id}', 'org1')")
    )
    [[organization_id]] = session.execute(
        text("SELECT id FROM organizations WHERE name=:org_name"), {"org_name": "org1"}
    )
    return org_id


def insert_submitter(session, org_id: UUID):
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
    return user_id


def insert_approver(session, org_id: UUID):
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
    return user_id


def test_can_check_organization_is_same(session):
    org_id = insert_org(session)
    submitter_id = insert_submitter(session, org_id=org_id)
    approver_id = insert_approver(session, org_id=org_id)

    approver = session.get(orm.UserORM, approver_id)

    user_repo = SqlAlchemyUserRepository(session)

    assert user_repo.is_same_organization(submitter_id, org_id)
    assert user_repo.is_same_organization(submitter_id, approver.organization_id)
    assert not user_repo.is_same_organization(submitter_id, uuid4())


def test_can_check_user_roles(
    session,
):
    org_id = insert_org(session)
    submitter_id = insert_submitter(session, org_id=org_id)
    approver_id = insert_approver(session, org_id=org_id)

    user_repo = SqlAlchemyUserRepository(session)

    assert user_repo.has_role(submitter_id, "SUBMITTER")
    assert user_repo.has_role(approver_id, "APPROVER")
    assert not user_repo.has_role(submitter_id, "APPROVER")


def test_can_check_existstance(session):
    org_id = insert_org(session)
    submitter_id = insert_submitter(session, org_id=org_id)

    user_repo = SqlAlchemyUserRepository(session)

    assert user_repo.exists(submitter_id)
    assert not user_repo.exists(uuid4())
