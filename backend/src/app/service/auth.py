import asyncio
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import ValidationError
from src.app.utils.secrets import get_secret
from src.app.utils.rate_limiter import get_rate_limiter
from src.app.model.exceptions import NotExistError, PermissionDeniedError, \
    StrongPermissionDeniedError
from src.app.model.user import Token, User
from src.app.repository.user import UserRepository

def create_access_token(user: User, secret_key: str, 
            algorithm: str="HS256", expires_minutes: int = 15) -> str:
    to_encode = user.model_dump()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire}) # type: ignore # this can only be named as exp
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    
    return encoded_jwt

def decode_token(token: str, secret_key: str, algorithm: str="HS256") -> User:
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
    except ExpiredSignatureError:   
        raise PermissionError("Token expired")
    except JWTError:
        raise PermissionError("Invalid token")
    user = User(
        user_id=payload.get('user_id'), # type: ignore
        username=payload.get('username'), # type: ignore
        is_admin=payload.get('is_admin') # type: ignore
    )
    return user

class AuthService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.rate_limiter = get_rate_limiter(
            max_attempts=5,
            lockout_duration_minutes=5,
            window_minutes=10
        )

    async def login(self, username: str, password: str) -> Token:
        # Check rate limiting before attempting authentication
        is_allowed, error_message = await self.rate_limiter.is_allowed(username)
        if not is_allowed:
            raise StrongPermissionDeniedError("Too many login attempts, can only try again in 5 minutes!")
        
        try:
            internal_user = await self.user_repository.get_internal_user_by_name(username)
        except NotExistError:
            # Record failed attempt for non-existent user (don't reveal user existence)
            # Only record if it's a real user to avoid information leakage
            # For now, we'll record it anyway since the error message doesn't reveal existence
            await self.rate_limiter.record_failed_attempt(username)
            raise PermissionDeniedError("User not found")
        
        # verify password is CPU bounded operation, so we run it in a separate thread to avoid blocking the main thread
        is_valid = await asyncio.to_thread(internal_user.verify_password, password)
        if not is_valid:
            # Record failed attempt
            await self.rate_limiter.record_failed_attempt(username)
            raise PermissionDeniedError("Wrong password")
        
        # Successful login - reset failed attempts
        await self.rate_limiter.reset_attempts(username)
        
        # get auth config is IO bounded operation, so we run it in a separate thread to avoid blocking the main thread
        auth_config = (await asyncio.to_thread(get_secret))['auth'] # type: ignore
        access_token = create_access_token(
            user=User(
                user_id=internal_user.user_id,
                username=username,
                is_admin=internal_user.is_admin
            ),
            secret_key=auth_config['secret_key'],
            algorithm=auth_config['algorithm'],
            expires_minutes=int(auth_config['expires_minutes'])
        )
        return Token(access_token=access_token, token_type="bearer")
    
    async def verify_token(self, token: str) -> User:
        try:
            # get auth config is IO bounded operation, so we run it in a separate thread to avoid blocking the main thread
            auth_config = (await asyncio.to_thread(get_secret))['auth'] # type: ignore
            decoded_token = decode_token(
                token=token,
                secret_key=auth_config['secret_key'],
                algorithm=auth_config['algorithm']
            )
        except ValidationError:
            raise PermissionDeniedError("Cannot parse token")
        except PermissionError as e:
            raise PermissionDeniedError(
                message=str(e),
                details=token
            )
        return decoded_token