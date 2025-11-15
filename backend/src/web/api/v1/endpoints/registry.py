from fastapi import APIRouter, Depends
from src.app.model.registry import Property
from src.app.service.registry import RegistryService
from src.web.dependency.service import get_registry_service
from src.web.dependency.auth import get_current_user, get_admin_user
from src.app.model.user import User
from src.app.model.market import PublicPropInfo

router = APIRouter(
    prefix="/registry",
    tags=["registry"],
)

@router.get("/registry/get_public_property")
async def get_public_property(
    property_id: str,
    registry_service: RegistryService = Depends(get_registry_service)
) -> Property:
    return await registry_service.get_public_property(property_id)

@router.get("/registry/get_private_property")
async def get_private_property(
    property_id: str,
    current_user: User = Depends(get_current_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> Property:
    return await registry_service.get_private_property(
        property_id, 
        current_user.user_id
    )
    
@router.get("/registry/list_private_properties")
async def list_private_properties(
    current_user: User = Depends(get_current_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> list[Property]:
    return await registry_service.list_private_properties(
        current_user.user_id
    )
    
@router.get("/registry/blurry_search_public")
async def blurry_search_public(
    keyword: str,
    limit: int = 10,
    registry_service: RegistryService = Depends(get_registry_service)
) -> list[Property]:
    return await registry_service.blurry_search_public(
        keyword,
        limit
    )
    
@router.get("/registry/blurry_search_yfinance")
async def blurry_search_yfinance(
    keyword: str,
    limit: int = 10,
    registry_service: RegistryService = Depends(get_registry_service)
) -> list[PublicPropInfo]:
    return await registry_service.blurry_search_yfinance(
        keyword,
        limit
    )
    
@router.post("/registry/register_public_property")
async def register_public_property(
    property: Property,
    admin_user: User = Depends(get_admin_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.register_public_property(
        property,
    )
    
@router.post("/registry/register_private_property")
async def register_private_property(
    property: Property,
    current_user: User = Depends(get_current_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.register_private_property(
        property,
        current_user.user_id
    )
    
@router.post("/registry/delist_public_property")
async def delist_public_property(
    property_id: str,
    admin_user: User = Depends(get_admin_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.delist_public_property(
        property_id
    )
    
@router.post("/registry/delist_private_property")
async def delist_private_property(
    property_id: str,
    current_user: User = Depends(get_current_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.delist_private_property(
        property_id,
        current_user.user_id
    )
    
@router.post("/registry/update_public_property")
async def update_public_property(
    property: Property,
    admin_user: User = Depends(get_admin_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.update_public_property(
        property
    )
    
@router.post("/registry/update_private_property")
async def update_private_property(
    property: Property,
    current_user: User = Depends(get_current_user),
    registry_service: RegistryService = Depends(get_registry_service)
) -> None:
    await registry_service.update_private_property(
        property,
        current_user.user_id
    )
    
@router.post("/registry/register_yfinance_property")
async def register_yfinance_property(
    symbol: str,
    registry_service: RegistryService = Depends(get_registry_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await registry_service.register_yfinance_property(
        symbol
    )
    
@router.post("/registry/register_yfinance_properties")
async def register_yfinance_properties(
    symbols: list[str],
    registry_service: RegistryService = Depends(get_registry_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await registry_service.register_yfinance_properties(
        symbols
    )