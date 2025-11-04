from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from src.app.model.user import User
from src.app.model.exceptions import PermissionDeniedError
from src.app.repository.user import UserRepository
from src.app.service.auth import AuthService
from src.web.dependency.repository import get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/management/login")

async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repository=user_repository)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.verify_token(token)

async def get_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise PermissionDeniedError("Admin user required")
    return user