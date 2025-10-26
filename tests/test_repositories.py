from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.expense_management.domain import model as expense_model
from src.iam.domain import model as user_model
from src._shared.infrastructure import orm
from src.expense_management.infrastructure import exception
from src.expense_management.infrastructure.repository import SqlAlchemyExpenseRepository
from src.iam.infrastructure.repository import SqlAlchemyUserRepository


def insert_org(session, commit: bool = False):
    org_id = uuid4()
    session.add(orm.OrganizationORM(id=org_id, name="org1"))
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


def generate_expense(submitter_id: UUID = uuid4(), org_id: UUID = uuid4()):
    return expense_model.Expense(
        submitter_id=submitter_id,
        date=datetime(2025, 1, 1),
        title="my expense",
        amount=100,
        category=expense_model.ExpenseCategory.OFFICE_SUPPLIES,
        organization_id=org_id,
    )


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
    def test_can_check_existance_persistance(self, postgres_session):
        org_id = insert_org(postgres_session, commit=True)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        postgres_session.commit()

        user_repo = SqlAlchemyUserRepository(postgres_session)

        assert user_repo.exists(submitter_id)
        assert not user_repo.exists(uuid4())

    def test_can_check_user_roles_persistant(
        self,
        postgres_session,
    ):
        org_id = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        approver_id = insert_approver(postgres_session, org_id=org_id)
        postgres_session.commit()

        user_repo = SqlAlchemyUserRepository(postgres_session)

        assert user_repo.has_role(submitter_id, "SUBMITTER")
        assert user_repo.has_role(approver_id, "APPROVER")
        assert not user_repo.has_role(submitter_id, "APPROVER")

    def test_can_check_organization_is_same(self, postgres_session):
        org_id = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        approver_id = insert_approver(postgres_session, org_id=org_id)
        approver = postgres_session.get(orm.UserORM, approver_id)
        postgres_session.commit()

        user_repo = SqlAlchemyUserRepository(postgres_session)

        assert user_repo.is_same_organization(submitter_id, org_id)
        assert user_repo.is_same_organization(submitter_id, approver.organization_id)
        assert not user_repo.is_same_organization(submitter_id, uuid4())


class TestPersistantExpenseRepo:
    def test_can_save_expense(self, postgres_session):
        expense_repo = SqlAlchemyExpenseRepository(postgres_session)
        org_id = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        expense = generate_expense(submitter_id=submitter_id, org_id=org_id)

        assert expense_repo.save(expense) is None

    def test_can_retrieve_existing_expense(self, postgres_session):
        expense_repo = SqlAlchemyExpenseRepository(postgres_session)
        org_id = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        expense = generate_expense(submitter_id=submitter_id, org_id=org_id)
        expense_repo.save(expense)
        assert expense_repo.get(expense.id) == expense

    def test_can_find_expenses_by_organization(self, postgres_session):
        expense_repo = SqlAlchemyExpenseRepository(postgres_session)
        org_id = insert_org(postgres_session)
        org_id2 = insert_org(postgres_session)
        submitter_id = insert_submitter(postgres_session, org_id=org_id)
        expenses = [
            generate_expense(submitter_id=submitter_id, org_id=org_id)
            for i in range(1000)
        ]
        postgres_session.commit()
        expenses.append(generate_expense(submitter_id=submitter_id, org_id=org_id2))
        for expense in expenses:
            expense_repo.save(expense)

        assert len(expense_repo.find_by_organization(org_id=org_id)) == 1000
        assert len(expense_repo.find_by_organization(org_id=org_id2)) == 1

    def test_exception_if_no_expense_found(self, postgres_session):
        expense_repo = SqlAlchemyExpenseRepository(postgres_session)
        with pytest.raises(exception.NoExpenseFound):
            expense_repo.get(uuid4())

        with pytest.raises(exception.NoExpenseFound):
            expense_repo.find_by_organization(uuid4())
