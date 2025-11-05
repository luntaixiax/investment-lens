from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Cookie
from typing import Optional
from src.app.model.user import User
from src.app.model.exceptions import PermissionDeniedError
from src.app.repository.user import UserRepository
from src.app.service.auth import AuthService
from src.web.dependency.repository import get_user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/management/login", auto_error=False)

async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repository=user_repository)

async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    access_token: str | None = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Get the current authenticated user.
    First tries to get token from cookie (for cookie-based auth),
    then falls back to Authorization header (for header-based auth).
    """
    # Try cookie first (for cookie-based authentication)
    token_value = access_token
    
    # Fall back to Authorization header if cookie not found
    if not token_value:
        token_value = token
    
    if not token_value:
        raise PermissionDeniedError(
            f"Not authenticated. Cookie present: {access_token is not None}, "
            f"Header token present: {token is not None}"
        )
    
    return await auth_service.verify_token(token_value)

async def get_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise PermissionDeniedError("Admin user required")
    return user