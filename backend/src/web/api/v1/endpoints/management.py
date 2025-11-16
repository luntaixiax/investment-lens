from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from src.app.service.auth import AuthService
from src.app.model.user import Token, UserCreate, User, UserRegister
from src.app.service.user import UserService
from src.web.dependency.service import get_user_service
from src.web.dependency.auth import get_admin_user, get_auth_service, get_current_user

router = APIRouter(prefix="/management", tags=["management"])


@router.post("/create_admin_user")
async def create_admin_user(
    user: UserRegister,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user) # this for existing admin access, not the user to create
) -> None:
    user_ = UserCreate(
        username=user.username,
        is_admin=True,
        email=user.email,
        password=user.password
    )
    await user_service.create_user(user_)
    
    
@router.post("/register")
async def register(
    user: UserRegister,
    user_service: UserService = Depends(get_user_service),
) -> None:
    # everyone can register, but only open to normal user
    user_ = UserCreate(
        username=user.username,
        is_admin=False,
        email=user.email,
        password=user.password
    )
    await user_service.create_user(user_)
    

@router.post("/login")
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    """Login the user and set the JWT as a cookie.
    The attacker can steal your JWT, send it to their own server, and impersonate your user until it expires.
    When you set a cookie like this, the browser stores it, but does not allow any JavaScript to read it.
    Only the browser itself can attach it automatically to outgoing requests to your backend (if CORS allows).
    So even if the frontend page has an XSS bug, the attacker cannot steal the token.
    """

    token_response = await auth_service.login(
        username=user_credentials.username, 
        password=user_credentials.password
    )
    response = JSONResponse(
        content={"message": "Login successful", "token_type": token_response.token_type}, 
    )
    response.set_cookie(
        key="access_token",
        value=token_response.access_token,
        httponly=True,
        secure=False,  # Set to False for development (HTTP). Use True in production (HTTPS)
        samesite="Lax"
    )
    return response

@router.get("/check_login")
async def check_login(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the user is logged in."""
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """Logout the authenticated user."""
    response = JSONResponse(
        content={"message": "Logout successful", "user_id": current_user.user_id}, 
    )
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Set to False for development (HTTP). Use True in production (HTTPS)
        samesite="Lax"
    )
    return response
    
@router.post("/remove_user")
async def remove_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await user_service.remove_user(user_id)
    
    
@router.post("/remove_user_by_name")
async def remove_user_by_name(
    username: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await user_service.remove_user_by_name(username)
    
@router.post("/update_user")
async def update_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await user_service.update_user(user)
    
@router.get("/get_user")
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> User:
    return await user_service.get_user(user_id)
    
@router.get("/get_user_by_name")
async def get_user_by_name(
    username: str,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> User:
    return await user_service.get_user_by_name(username)

@router.get("/list_user")
async def list_user(
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(get_admin_user)
) -> list[User]:
    return await user_service.list_user()

@router.get("/request_reset_password")
async def request_reset_password(
    email: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.request_reset_password(email)
    
@router.post("/validate_reset_password_token")
async def validate_reset_password_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.validate_reset_password_token(token)

@router.post("/reset_password")
async def reset_password(
    token: str,
    new_password: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.reset_password(token, new_password)