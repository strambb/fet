
from datetime import datetime, timedelta

import pytz
from src.domain.model import Expense, Period

tz_berlin = pytz.timezone('Europe/Berlin')



def test_init_period_with_balance():
    period = Period(initial_balance=100)
    assert period.balance - 100 < 1e-8


def test_add_expense_to_period_increases_total():
    start = datetime(year=2025, month=1, day=1, tzinfo=tz_berlin)
    expense_date = datetime(2025,2, 1)
    period = Period(start=start, end=start + timedelta(days=365), initial_balance=100.10)
    expense = Expense(expenseid="expense-uuid", title="My Expense", notes="No notes for this expense", amount=100.00, category="Furniture", expense_date=expense_date)

    assert period.balance - 100.10 < 1e-8
    period.add_expense(expense)
    assert period.balance - 0.10 < 1e-8
    assert period.expenses - 100 < 1e-8