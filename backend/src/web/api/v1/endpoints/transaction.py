from fastapi import APIRouter, Depends
from src.app.model.transaction import TransactionCreate, Transaction
from src.app.service.transaction import TransactionService
from src.web.dependency.service import get_transaction_service
from src.web.dependency.auth import get_current_user
from src.app.model.user import User

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.post("/add_transaction")
async def add_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
) -> None:
    await transaction_service.add_transaction(transaction, current_user.user_id)
    
@router.get("/get_transaction")
async def get_transaction(
    trans_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
) -> Transaction:
    return await transaction_service.get_transaction(trans_id, current_user.user_id)
    
@router.delete("/remove_transaction")
async def remove_transaction(
    trans_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
) -> None:
    await transaction_service.remove_transaction(trans_id, current_user.user_id)
    
@router.put("/update_transaction")
async def update_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user)
) -> None:
    await transaction_service.update_transaction(transaction, current_user.user_id)