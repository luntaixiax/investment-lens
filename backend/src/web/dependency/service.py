from fastapi import Depends
from src.app.repository.user import UserRepository
from src.app.service.user import UserService
from src.web.dependency.repository import get_user_repository
from src.app.repository.market import FxRepository
from src.app.service.market import FxService
from src.web.dependency.repository import get_fx_repository

async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository=user_repository)

async def get_fx_service(
    fx_repository: FxRepository = Depends(get_fx_repository)
) -> FxService:
    return FxService(fx_repository=fx_repository)