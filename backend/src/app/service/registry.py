from src.app.repository.registry import PropertyRepository, PrivatePropOwnershipRepository
from src.app.model.registry import Property, PrivatePropOwnership
from src.app.model.exceptions import AlreadyExistError, NotExistError, OpNotPermittedError, \
    FKNoDeleteUpdateError, PermissionDeniedError

class RegistryService:
    
    def __init__(self, 
            property_repository: PropertyRepository, 
            private_prop_ownership_repository: PrivatePropOwnershipRepository
        ):
        self.property_repository = property_repository
        self.private_prop_ownership_repository = private_prop_ownership_repository
        
    async def register_public_property(self, property: Property):
        if property.is_public:
            try:
                await self.property_repository.add(property)
            except AlreadyExistError as e:
                raise AlreadyExistError(
                    f"Property {property} already exist",
                    details="N/A" # don't pass database info
                )
        else:
            raise OpNotPermittedError(f"Property {property} is not public")
        
    async def register_private_property(self, property: Property, user_id: str):
        if not property.is_public:
            ownership = PrivatePropOwnership(prop_id=property.prop_id, user_id=user_id)
            try:
                # add property first
                try:
                    await self.property_repository.add(property)
                except AlreadyExistError as e:
                    raise AlreadyExistError(
                        f"Property {property} already exist",
                        details="N/A" # don't pass database info
                    )
                # then add ownership
                await self.private_prop_ownership_repository.add(ownership)
            except AlreadyExistError as e:
                raise AlreadyExistError(
                    f"Property {property} is already owned by someone else",
                    details="N/A" # don't pass database info
                )
        else:
            raise OpNotPermittedError(f"Property {property} is public")


    async def delist_public_property(self, prop_id: str):
        # make sure the property is public and exists
        property = await self.get_public_property.get(prop_id)
        try:
            await self.property_repository.remove(prop_id)
        except NotExistError as e:
            raise NotExistError(
                f"Property {prop_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Property {prop_id} is associated with other data, cannot delete",
                details=e.details
            )
            
    async def delist_private_property(self, prop_id: str, user_id: str):
        # make sure the property is private and exists
        property = await self.get_private_property(prop_id, user_id)
        try:
            # first remove ownership
            try:
                await self.private_prop_ownership_repository.remove_by_prop_id(prop_id)
            except NotExistError as e:
                raise NotExistError(
                    f"Property {prop_id} is not owned by user {user_id}",
                    details="N/A" # don't pass database info
                )
            except FKNoDeleteUpdateError as e:
                raise FKNoDeleteUpdateError(
                    f"Ownership of property {prop_id} is associated with other data, cannot delete",
                    details=e.details
                )
            # then remove property
            await self.property_repository.remove(prop_id)
        except NotExistError as e:
            raise NotExistError(
                f"Property {prop_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Property {prop_id} is associated with other data, cannot delete",
                details=e.details
            )
        
    async def update_public_property(self, property: Property):
        # make sure the property is public and exists
        existing_property = await self.get_public_property(property.prop_id)
        # make sure symbol, and currency, public flag are the same as the existing property
        if existing_property.symbol != property.symbol:
            raise OpNotPermittedError(
                f"Should not change symbol of public property", 
                details=f"Existing symbol: {existing_property.symbol}, New symbol: {property.symbol}"
            )
        if existing_property.currency != property.currency:
            raise OpNotPermittedError(
                f"Should not change currency of public property", 
                details=f"Existing currency: {existing_property.currency}, New currency: {property.currency}"
            )
        if existing_property.is_public != property.is_public:
            raise OpNotPermittedError(
                f"Should not change public flag of public property", 
                details=f"Existing public flag: {existing_property.is_public}, New public flag: {property.is_public}"
            )
            
        try:
            await self.property_repository.update(property)
        except NotExistError as e:
            raise NotExistError(f"Property {property.prop_id} does not exist", details="N/A")
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Property {property.prop_id} is associated with other data, cannot update", details=e.details
            )
            
    async def update_private_property(self, property: Property, user_id: str):
        # make sure the property is private and exists
        existing_property = await self.get_private_property(property.prop_id, user_id)
        # make sure symbol, and currency, public flag are the same as the existing property
        if existing_property.symbol != property.symbol:
            raise OpNotPermittedError(
                f"Should not change symbol of private property", 
                details=f"Existing symbol: {existing_property.symbol}, New symbol: {property.symbol}"
            )
        if existing_property.currency != property.currency:
            raise OpNotPermittedError(
                f"Should not change currency of private property", 
                details=f"Existing currency: {existing_property.currency}, New currency: {property.currency}"
            )
        if existing_property.is_public != property.is_public:
            raise OpNotPermittedError(
                f"Should not change public flag of private property", 
                details=f"Existing public flag: {existing_property.is_public}, New public flag: {property.is_public}"
            )
            
        try:
            await self.property_repository.update(property)
        except NotExistError as e:
            raise NotExistError(f"Property {property.prop_id} does not exist", details="N/A")
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Property {property.prop_id} is associated with other data, cannot update", details=e.details
            )
        
        
    async def get_public_property(self, prop_id: str) -> Property:
        try:
            property = await self.property_repository.get(prop_id)
        except NotExistError as e:
            raise NotExistError(
                f"Property {prop_id} does not exist",
                details="N/A" # don't pass database info
            )
        else:
            if property.is_public:
                return property
            else:
                raise OpNotPermittedError(f"Property {prop_id} is private")
                
    async def get_private_property(self, prop_id: str, user_id: str) -> Property:
        try:
            property = await self.property_repository.get(prop_id)
        except NotExistError as e:
            raise NotExistError(
                f"Property {prop_id} does not exist",
                details="N/A" # don't pass database info
            )
        else:
            if property.is_public:
                raise OpNotPermittedError(f"Property {prop_id} is public")
            else:
                try:
                    ownership = await self.private_prop_ownership_repository.get_by_prop_id(prop_id)
                except NotExistError as e:
                    raise NotExistError(
                        f"Property {prop_id} is not owned by user {user_id}",
                        details="N/A" # don't pass database info
                    )
                    
                if ownership.user_id == user_id:
                    return property
                else:
                    raise OpNotPermittedError(f"Property {prop_id} is not owned by user {user_id}")
                
    async def list_private_properties(self, user_id: str) -> list[Property]:
        private_prop_ownerships = await self.private_prop_ownership_repository.list_by_user(user_id)
        prop_ids = [ownership.prop_id for ownership in private_prop_ownerships]
        properties = await self.property_repository.gets(prop_ids)
        return properties
    
    async def blurry_search_public(self, keyword: str, limit: int = 10) -> list[Property]:
        return await self.property_repository.blurry_search_public(keyword, limit)