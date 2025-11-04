from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.app.service.auth import AuthService
from src.app.model.user import Token, UserCreate, User, UserRegister
from src.app.service.user import UserService
from src.web.dependency.service import get_user_service
from src.web.dependency.auth import get_admin_user, get_auth_service

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
        password=user.password
    )
    await user_service.create_user(user_)
    

@router.post("/login", response_model=Token)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    return await auth_service.login(
        username=user_credentials.username, 
        password=user_credentials.password
    )
    
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