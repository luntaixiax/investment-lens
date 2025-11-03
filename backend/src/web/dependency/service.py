from fastapi import Depends
from src.app.repository.user import UserRepository
from src.app.service.user import UserService
from src.web.dependency.repository import get_user_repository

async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository=user_repository)