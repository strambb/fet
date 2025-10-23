from uuid import UUID
from typing import Optional
from src.infrastructure import exception
from src.domain import repositories
from src.domain.expense import model as expense_model
from src.domain.user import model as user_model
from sqlalchemy.orm import Session
from src.infrastructure import orm

### User repos
class SqlAlchemyUserRepository(repositories.IUserRepository):
    def __init__(self, session: Session):
        self._session = session

    def has_role(self, user_id: UUID, role: str) -> bool:
        user_orm = self._session.get(orm.UserORM, user_id)
        return user_orm.role.name == role if user_orm else False

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool:
        user_orm = self._session.get(orm.UserORM, user_id)
        return user_orm.organization_id == org_id if user_orm else False

    def exists(self, user_id: UUID):
        return self._session.get(orm.UserORM, user_id) is not None

class FakeUserRepository(repositories.IUserRepository):
    def __init__(self, users: Optional[list[user_model.User]] = None):
        self._users = {user.id: user for user in users} if users else {}

    def has_role(self, user_id: UUID, role: str) -> bool:
        user = self._users.get(user_id, None)
        return user.role.name == role if user else False

    def is_same_organization(self, user_id: UUID, org_id: UUID) -> bool:
        user = self._users.get(user_id, None)
        return user.organization_id == org_id if user else False

    def exists(self, user_id):
        return user_id in self._users

#### Expense Repos
class SqlAlchemyExpenseRepository(repositories.IExpenseRepository):
    def __init__(self, session: Session):
        self._session = session

    def get(self, expense_id: UUID):
        expense_orm = self._session.get(orm.ExpenseORM, expense_id)
        if not expense_orm:
            raise exception.NoExpenseFound

        return expense_orm.to_domain()

    def save(self, expense):
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


class FakeExpenseRepository(repositories.IExpenseRepository):
    def __init__(self, expenses: Optional[list[expense_model.Expense]] = None):
        self._expenses = (
            {expense.id: expense for expense in expenses} if expenses else {}
        )

    def get(self, expense_id: UUID) -> expense_model.Expense:
        expense = self._expenses.get(expense_id, None)
        if not expense:
            raise exception.NoExpenseFound
        return expense

    def save(self, expense) -> None:
        self._expenses[expense.id] = expense

    def find_by_organization(self, org_id: UUID) -> list[expense_model.Expense]:
        expenses = [
            expense
            for expense in self._expenses.values()
            if expense.organization.id == org_id
        ]
        if not expenses:
            raise exception.NoExpenseFound
        return expenses
