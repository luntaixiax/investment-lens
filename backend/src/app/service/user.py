from src.app.model.user import UserCreate, User
from src.app.repository.user import UserRepository
from src.app.model.exceptions import AlreadyExistError, NotExistError, FKNoDeleteUpdateError

class UserService:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    async def create_user(self, user: UserCreate):
        try:
            await self.user_repository.add(user)
        except AlreadyExistError as e:
            raise AlreadyExistError(
                f"User {user.username} already exist",
                details="N/A" # don't pass database info
            )
        
    async def remove_user(self, user_id: str):
        try:
            await self.user_repository.remove(user_id)
        except NotExistError as e:
            raise NotExistError(
                f"User {user_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"User {user_id} is associated with other data, cannot delete",
                details=e.details
            )
            
    async def remove_user_by_name(self, username: str):
        try:
            await self.user_repository.remove_by_name(username)
        except NotExistError as e:
            raise NotExistError(
                f"User {username} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"User {username} is associated with other data, cannot delete",
                details=e.details
            )
        
        
    async def update_user(self, user: UserCreate):
        try:
            await self.user_repository.update(user)
        except NotExistError as e:
            raise NotExistError(
                f"User {user.username} does not exist",
                details="N/A" # don't pass database info 
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"User {user} is associated with other data, cannot update",
                details=e.details
            )
        
    async def get_user(self, user_id: str) -> User:
        try:
            return await self.user_repository.get(user_id)
        except NotExistError as e:
            raise NotExistError(
                f"User {user_id} does not exist",
                details="N/A" # don't pass database info
            )
            
    async def get_user_by_name(self, username: str) -> User:
        try:
            return await self.user_repository.get_by_name(username)
        except NotExistError as e:
            raise NotExistError(
                f"User {username} does not exist",
                details="N/A" # don't pass database info
            )
        
    async def list_user(self) -> list[User]:
        return await self.user_repository.list_user()