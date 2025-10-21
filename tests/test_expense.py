import pytest

from datetime import datetime, timedelta
from uuid import uuid4
import pytz
import src.domain.expense.model as model
import src.domain.expense.exception as exception
from random import randint

tz_berlin = pytz.timezone("Europe/Berlin")


# def test_init_period_with_balance():
#     period = Period(initial_balance=100)
#     assert period.balance - 100 < 1e-8


# def test_add_expense_to_period_increases_total():
#     start = datetime(year=2025, month=1, day=1, tzinfo=tz_berlin)
#     expense_date = datetime(2025, 2, 1)
#     period = Period(
#         start=start, end=start + timedelta(days=365), initial_balance=100.10
#     )
#     expense = Expense(
#         expenseid="expense-uuid",
#         title="My Expense",
#         notes="No notes for this expense",
#         amount=100.00,
#         category="Furniture",
#         expense_date=expense_date,
#     )

#     assert period.balance - 100.10 < 1e-8
#     period.add_expense(expense)
#     assert period.balance - 0.10 < 1e-8
#     assert period.expenses - 100 < 1e-8


def random_submitter():
    return f"submitter-{str(uuid4())[-6:]}"


def random_org():
    name = f"org-{str(uuid4())[-6:]}"
    return model.Organization(name=name)


def generate_random_expense(amount: float = 10):
    return model.Expense(
        submitter_id=random_submitter(),
        date=datetime(2025, 1, randint(1, 31)),
        title=f"title-{str(uuid4())[-6:]}",
        amount=amount,
        category=model.ExpenseCategory.OFFICE_SUPPLIES,
        organization=random_org(),
    )


def test_new_expense_in_draft_state():
    org = model.Organization(name="FraktionA")
    expense = model.Expense(
        submitter_id="me",
        category=model.ExpenseCategory.OFFICE_SUPPLIES,
        title="Pens",
        amount=100,
        document_reference=None,
        organization=org,
        date=datetime(2025, 2, 1),
    )
    assert expense.state == model.ExpenseState.DRAFT


def test_expense_after_submit_in_submitted_state():
    expense = generate_random_expense()
    expense.submit()
    assert expense.state == model.ExpenseState.SUBMITTED


def test_cannot_submit_expense_if_not_draft():
    expense = generate_random_expense()
    expense.submit()
    with pytest.raises(exception.ExpenseNotDraft):
        expense.submit()


def test_expense_error_approval_in_draft_state():
    expense = generate_random_expense()
    with pytest.raises(exception.ExpenseNotSubmitted):
        expense.approve("valid_approver_id")


def test_cannot_self_approve():
    expense = generate_random_expense()
    expense.submit()
    with pytest.raises(exception.InvalidApprover):
        expense.approve(expense.submitter_id)


def test_expense_approval_by_valid_approver():
    expense = generate_random_expense()
    expense.submit()
    expense.approve("valid_approver_id")
    assert expense.state == model.ExpenseState.APPROVED


def test_can_withdraw_expense_from_draft_as_submitter():
    expense1 = generate_random_expense()

    # Expense in draft and withdraw
    submitter1 = expense1.submitter_id
    expense1.withdraw(submitter1)

    assert expense1.state == model.ExpenseState.WITHDRAWN


def test_can_withdraw_expense_from_submitted_as_submitter():
    expense1 = generate_random_expense()

    # Expense in draft and withdraw
    submitter1 = expense1.submitter_id
    expense1.submit()
    expense1.withdraw(submitter1)

    assert expense1.state == model.ExpenseState.WITHDRAWN


def test_cannot_withdraw_as_different_user():
    expense = generate_random_expense()

    with pytest.raises(exception.InvalidWithdrawUser):
        expense.withdraw("other_user")


def test_cannot_withdraw_from_approved_state():
    expense = generate_random_expense()
    expense.submit()
    expense.approve("valid_approver")
    with pytest.raises(exception.InvalidWithdrawState):
        expense.withdraw(expense.submitter_id)


def test_can_revoke_approval_as_approver_with_reason():
    expense = generate_random_expense()
    expense.submit()
    approver = "valid_approver"
    expense.approve(approver)
    expense.revoke(by=approver, reason="new insights")
    assert expense.state == model.ExpenseState.REVOKED


def test_cannot_revoce_approval_as_approver_without_reason():
    expense = generate_random_expense()
    expense.submit()
    approver = "valid_approver"
    expense.approve(approver)
    with pytest.raises(exception.MissingReason):
        expense.revoke(by=approver, reason=str())

    with pytest.raises(exception.MissingReason):
        expense.revoke(by=approver, reason="")

    assert expense.state == model.ExpenseState.APPROVED


def test_cannot_revoke_approval_as_not_approver():
    expense = generate_random_expense()
    expense.submit()
    approver = "valid_approver"
    expense.approve(approver)
    with pytest.raises(exception.InvalidRevokeUser):
        expense.revoke("not_approver", reason="good reason")


def test_can_decline_in_submitted_state_as_not_submitter():
    raise NotImplementedError


def test_can_approve_if_budget_is_greater_expense():
    raise NotImplementedError


def test_cannot_approve_if_budget_is_smaller_than_expense():
    raise NotImplementedError
