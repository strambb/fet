from uuid import UUID
from typing import Optional
from src.expense_management.infrastructure import exception
from src.expense_management.domain import repository
from src.expense_management.domain import model as expense_model
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src._shared.infrastructure import orm


#### Expense Repos
class SqlAlchemyExpenseRepository(repository.IExpenseRepository):
    def __init__(self, session: Session):
        self._session = session

    def get(self, expense_id: UUID):
        expense_orm = self._session.get(orm.ExpenseORM, expense_id)
        if not expense_orm:
            raise exception.NoExpenseFound

        return expense_orm.to_domain()

    def save(self, expense: expense_model.Expense):
        expense_orm = orm.ExpenseORM.from_domain(expense)

        self._session.add(expense_orm)
        self._session.commit()

    def find_by_organization(self, org_id: UUID) -> list[expense_model.Expense]:
        expense_orms = (
            self._session.query(orm.ExpenseORM).filter_by(organization_id=org_id).all()
        )
        if not expense_orms:
            raise exception.NoExpenseFound

        return [expense_orm.to_domain() for expense_orm in expense_orms]

    def find_by_user(self, user_id: UUID) -> list[expense_model.Expense]:
        expense_orms = (
            self._session.query(orm.ExpenseORM)
            .filter(
                or_(
                    orm.ExpenseORM.submitter_id == user_id,
                    orm.ExpenseORM.approved_by_id == user_id,
                )
            )
            .all()
        )
        if not expense_orms:
            raise exception.NoExpenseFound

        return [expense_orm.to_domain() for expense_orm in expense_orms]


class FakeExpenseRepository(repository.IExpenseRepository):
    def __init__(self, expenses: Optional[list[expense_model.Expense]] = None):
        self._expenses = (
            {expense.id: expense for expense in expenses} if expenses else {}
        )

    def get(self, expense_id: UUID) -> expense_model.Expense:
        expense = self._expenses.get(expense_id, None)
        if not expense:
            raise exception.NoExpenseFound
        return expense

    def save(self, expense: expense_model.Expense) -> None:
        self._expenses[expense.id] = expense

    def find_by_organization(self, org_id: UUID) -> list[expense_model.Expense]:
        expenses = [
            expense
            for expense in self._expenses.values()
            if expense.organization_id == org_id
        ]
        if not expenses:
            raise exception.NoExpenseFound
        return expenses

    def find_by_user(self, user_id: UUID) -> list[expense_model.Expense]:
        expenses = [
            expense
            for expense in self._expenses.values()
            if expense.submitter_id == user_id or expense.approved_by_id == user_id
        ]
        if not expenses:
            raise exception.NoExpenseFound
        return expenses
