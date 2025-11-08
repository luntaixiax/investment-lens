from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine, create_engine
from fastapi import Depends
from src.app.repository.user import UserRepository
from src.app.utils.secrets import get_async_db_url, get_sync_db_url
from src.app.repository.market import FxRepository
# Global state for caching engine and sessionmaker
_async_engine: AsyncEngine | None = None
_async_session_maker: sessionmaker[AsyncSession] | None = None

async def get_async_engine(db: str = 'primary') -> AsyncEngine:
    """
    Get an async engine (cached globally for efficiency).
    
    Creates the engine once and reuses it for all subsequent requests.

    Args:
        db (str): The database name.

    Returns:
        AsyncEngine: The async engine.
    """
    global _async_engine
    
    if _async_engine is None:
        db_url = await get_async_db_url(db)
        _async_engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            pool_size=15, # Base pool size
            max_overflow=5,   # Extra connections when pool is full (explicit)
            pool_pre_ping=True, # Verify connection before using (prevents stale connections)
            pool_recycle=3600, # Recycle connections after 1 hour
        )
    return _async_engine

@lru_cache(maxsize=1)
def get_sync_engine(db: str = 'primary') -> Engine:
    """
    Get a sync engine (cached for efficiency).

    Args:
        db (str): The database name.

    Returns:
        Engine: The sync engine.
    """
    db_url = get_sync_db_url(db)
    sync_engine = create_engine(db_url, pool_size=10, echo=False)
    return sync_engine


async def get_async_session() -> AsyncSession:
    """
    Get an async session.
    
    Creates sessionmaker once and reuses it for all requests.

    Returns:
        AsyncSession: The async session.
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        async_engine = await get_async_engine()
        _async_session_maker = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async with _async_session_maker() as session:
        yield session
        
        
async def get_user_repository(
    async_session: AsyncSession = Depends(get_async_session)
) -> UserRepository:
    return UserRepository(db_session=async_session)

async def get_fx_repository(
    async_session: AsyncSession = Depends(get_async_session)
) -> FxRepository:
    return FxRepository(db_session=async_session)
        
        
if __name__ == "__main__":
    from sqlalchemy_utils import database_exists, create_database, drop_database
    from sqlalchemy import create_engine
    from src.app.repository.orm import SQLModelWithSort
    from src.app.utils.secrets import get_sync_engine
    
    sync_engine = get_sync_engine()
    
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)
        
    SQLModelWithSort.create_table_within_collection(
        collection='primary',
        engine=sync_engine
    )