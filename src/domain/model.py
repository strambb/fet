from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional




class Expense:
    def __init__(self, expenseid:str, title: str, amount: float, category:str, expense_date: datetime, notes: Optional[str] = None):
        self.expenseid = expenseid
        self.title = title
        self._amount =  amount
        self._category = category
        self._expense_date = expense_date
        self.notes = notes
        
    @property
    def amount(self):
        return self._amount
    
    @property
    def expense_date(self):
        return self._expense_date
        

class Period:
    def __init__(self, start: Optional[datetime]=None, end: Optional[datetime] = None, initial_balance: float = 0, ):
        if start is None:
            start = datetime(year=datetime.now().year, month=1, day=1)
        if end is None:
            end = start + relativedelta(years=1)
        self._start = start
        self._end = end
        self._inital_balance = initial_balance
        self._expenses = []

    
    @property
    def expenses(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> float:
        if not start or not end:
            return sum(expense.amount for expense in self._expenses)
        filtered = filter(lambda x: x.expense_date >= start and x.expense_date <= end, self._expenses)
        return sum(expense.amount for expense in filtered)


    @property
    def balance(self) -> float:
        return self._inital_balance - self.expenses
    

    def add_expense(self, expense: Expense):
        self._expenses.append(expense)
