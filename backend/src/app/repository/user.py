from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlmodel import delete, select
from src.app.repository.orm import UserORM
from src.app.model.user import User, UserCreate, UserInternalRead
from src.app.model.exceptions import AlreadyExistError, FKNoDeleteUpdateError, NotExistError

class UserRepository:
    
    def __init__(self, db_session: AsyncSession):
        """Initialize the user DAO.
        
        Args:
            db_session (AsyncSession): The SQLAlchemy async session.
        """
        self.db_session = db_session
        
    def fromUser(self, user: UserCreate) -> UserORM:
        """Convert UserCreate to UserORM.
        
        Args:
            user (UserCreate): The UserCreate object.
            
        Returns:
            UserORM: The UserORM object.
        """
        return UserORM(
            user_id = user.user_id,
            username = user.username,
            hashed_password = user.hashed_password, # type: ignore
            is_admin = user.is_admin,
            email = user.email
        )
        
    def toUser(self, user_orm: UserORM) -> User:
        """Convert UserORM to User.
        
        Args:
            user_orm (UserORM): The UserORM object.
            
        Returns:
            User: The User object.
        """
        return User(
            user_id = user_orm.user_id,
            username = user_orm.username,
            is_admin = user_orm.is_admin,
            email = user_orm.email
        )
        
    async def add(self, user: UserCreate):
        """Add a user to the database.
        
        Args:
            user (UserCreate): The UserCreate object.
        """
        user_orm = self.fromUser(user)
        self.db_session.add(user_orm)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(details=str(e))
        
    async def remove(self, user_id: str):
        """Remove a user from the database.
        
        Args:
            user_id (str): The ID of the user to remove.
        """
        sql = delete(UserORM).where(UserORM.user_id == user_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def remove_by_name(self, username: str):
        """Remove a user from the database by name.
        
        Args:
            username (str): The name of the user to remove.
        """
        sql = delete(UserORM).where(UserORM.username == username)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def update(self, user: UserCreate):
        """Update a user in the database.
        
        Args:
            user (UserCreate): The UserCreate object.
        """
        user_orm = self.fromUser(user)
        
        sql = select(UserORM).where(UserORM.user_id == user.user_id)
        try:
            result = await self.db_session.execute(sql) # get the ccount
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        
        if not p == user_orm:
            # update
            p.username = user_orm.username
            p.hashed_password = user_orm.hashed_password # type: ignore
            p.is_admin = user_orm.is_admin
            p.email = user_orm.email
            
            self.db_session.add(p)
            await self.db_session.commit()
            await self.db_session.refresh(p) # update p to instantly have new values
            
    async def get(self, user_id: str) -> User:
        """Get a user from the database.
        
        Args:
            user_id (str): The ID of the user to get.
            
        Returns:
            User: The User object.
        """
        sql = select(UserORM).where(UserORM.user_id == user_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.toUser(p)
            
    async def get_by_name(self, username: str) -> User:
        """Get a user from the database by name.
        
        Args:
            username (str): The name of the user to get.
            
        Returns:
            User: The User object.
        """
        sql = select(UserORM).where(UserORM.username == username)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.toUser(p)
    
    async def get_by_email(self, email: str) -> User:
        """Get a user from the database by email.
        
        Args:
            email (str): The email of the user to get.
            
        Returns:
            User: The User object.
        """
        sql = select(UserORM).where(UserORM.email == email)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.toUser(p)
    
    async def get_internal_user_by_name(self, username: str) -> UserInternalRead:
        """Get an internal user from the database by name.
        
        Args:
            username (str): The name of the user to get.
            
        Returns:
            UserInternalRead: The UserInternalRead object.
        """
        sql = select(UserORM).where(UserORM.username == username)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return UserInternalRead(
            **self.toUser(p).model_dump(),
            hashed_password=p.hashed_password
        )
    
    async def list_user(self) -> list[User]:  
        """List all users from the database.
        
        Returns:
            list[User]: The list of User objects.
        """
        sql = select(UserORM)
        result = await self.db_session.execute(sql)
        users = result.scalars().all() # convert to list of UserORM (flat list by scalars)
        return [self.toUser(u) for u in users]