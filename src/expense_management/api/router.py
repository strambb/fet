from fastapi.routing import APIRouter



router = APIRouter(prefix="expenses")



@router.get("/{expense_id}", )
def get_expense_by_id():
    pass


