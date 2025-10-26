from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional
from enum import Enum, auto
from dataclasses import dataclass, field
from uuid import uuid4, UUID
import src.expense_management.domain.exception as exception


class ExpenseState(Enum):
    DRAFT = auto()
    SUBMITTED = auto()
    APPROVED = auto()
    WITHDRAWN = auto()
    REVOKED = auto()


class ExpenseCategory(Enum):
    OFFICE_SUPPLIES = auto()


@dataclass(kw_only=True)
class Expense:
    id: UUID = field(default_factory=uuid4)
    submitter_id: UUID
    date: datetime
    title: str
    amount: float
    category: ExpenseCategory
    organization_id: UUID
    notes: Optional[str] = None
    state: ExpenseState = ExpenseState.DRAFT
    document_reference: Optional[str] = None
    approved_by_id: Optional[UUID] = None
    decline_reason: Optional[str] = None
    revoke_reason: Optional[str] = None

    def submit(self, by: UUID):
        if not self._ensure(self.submitter_id == by):
            raise exception.InvalidSubmitUser

        if not self._ensure(self.state == ExpenseState.DRAFT):
            raise exception.ExpenseNotDraft

        self.state = ExpenseState.SUBMITTED

    def approve(self, by: UUID):
        if not self._ensure(self.state == ExpenseState.SUBMITTED):
            raise (exception.ExpenseNotSubmitted)

        if not self._ensure(self.submitter_id != by):
            raise (exception.InvalidApprover)

        self.approved_by_id = by
        self.state = ExpenseState.APPROVED

    def withdraw(self, by: UUID):
        if not self._ensure(self.submitter_id == by):
            raise exception.InvalidWithdrawUser

        if not self._ensure(self.state in [ExpenseState.DRAFT, ExpenseState.SUBMITTED]):
            raise exception.InvalidWithdrawState

        self.state = ExpenseState.WITHDRAWN

    def revoke(self, by: UUID, reason: str):
        if not reason:
            raise exception.MissingReason

        if not self._ensure(self.state == ExpenseState.APPROVED):
            raise exception.InvalidRevokeState

        if not self._ensure(self.approved_by_id == by):
            raise exception.InvalidRevokeUser

        self.revoke_reason = reason
        self.state = ExpenseState.REVOKED

    # helper
    def _ensure(self, condition) -> bool:
        return condition


class Period:
    def __init__(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        initial_balance: float = 0,
    ):
        if start is None:
            start = datetime(year=datetime.now().year, month=1, day=1)
        if end is None:
            end = start + relativedelta(years=1)
        self._start = start
        self._end = end
        self._inital_balance = initial_balance
        self._expenses = []

    @property
    def expenses(
        self, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> float:
        if not start or not end:
            return sum(expense.amount for expense in self._expenses)
        filtered = filter(
            lambda x: x.expense_date >= start and x.expense_date <= end, self._expenses
        )
        return sum(expense.amount for expense in filtered)

    @property
    def balance(self) -> float:
        return self._inital_balance - self.expenses

    def add_expense(self, expense: Expense):
        self._expenses.append(expense)
