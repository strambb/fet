class ExpenseNotSubmitted(Exception):
    pass


class InvalidApprover(Exception):
    pass


class ExpenseNotDraft(Exception):
    pass


class InvalidWithdrawUser(Exception):
    pass


class InvalidWithdrawState(Exception):
    pass


class InvalidRevokeState(Exception):
    pass


class InvalidRevokeUser(Exception):
    pass


class MissingReason(Exception):
    pass
