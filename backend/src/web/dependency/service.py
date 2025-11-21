from fastapi import Depends
from src.app.repository.user import UserRepository
from src.app.service.user import UserService
from src.web.dependency.repository import get_user_repository
from src.app.repository.market import FxRepository
from src.app.service.market import FxService
from src.web.dependency.repository import get_fx_repository
from src.app.service.market import YFinanceService
from src.app.repository.registry import PropertyRepository, \
    PrivatePropOwnershipRepository, AccountRepository
from src.app.service.registry import RegistryService, AccountService
from src.app.service.email import EmailService
from src.web.dependency.repository import get_property_repository, \
    get_private_prop_ownership_repository, get_account_repository

async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository=user_repository)

async def get_fx_service(
    fx_repository: FxRepository = Depends(get_fx_repository)
) -> FxService:
    return FxService(fx_repository=fx_repository)

async def get_yfinance_service() -> YFinanceService:
    return YFinanceService()

async def get_registry_service(
    property_repository: PropertyRepository = Depends(get_property_repository),
    private_prop_ownership_repository: PrivatePropOwnershipRepository = Depends(get_private_prop_ownership_repository),
    yfinance_service: YFinanceService = Depends(get_yfinance_service)
) -> RegistryService:
    return RegistryService(
        property_repository=property_repository, 
        private_prop_ownership_repository=private_prop_ownership_repository,
        yfinance_service=yfinance_service
    )
    
async def get_email_service() -> EmailService:
    return EmailService()

async def get_account_service(
    account_repository: AccountRepository = Depends(get_account_repository)
) -> AccountService:
    return AccountService(account_repository=account_repository)