from datetime import timedelta
from yokedcache import cached
from src.app.model.transaction import Leg, LegCreate
from src.app.repository.transaction import TransactionBodyRepository, LegRepository
from src.app.model.transaction import TransactionCreate, Transaction
from src.app.model.exceptions import OpNotPermittedError, AlreadyExistError, FKNotExistError, NotExistError, FKNoDeleteUpdateError
from src.app.repository.cache import cache
from src.app.utils.cache import deserialize_cached_model

class TransactionService:
    
    def __init__(
        self, 
        transaction_body_repository: TransactionBodyRepository, 
        leg_repository: LegRepository,
    ):
        self.transaction_body_repository = transaction_body_repository
        self.leg_repository = leg_repository
        
    async def add_transaction(self, transaction: TransactionCreate, user_id: str):
        if transaction.user_id != user_id:
            raise OpNotPermittedError(
                f"Transaction user ID {transaction.user_id} must be the same as the user ID {user_id}",
                details="N/A" # don't pass database info
            )
        
        # add transaction body first
        try:
            await self.transaction_body_repository.add(
                transaction.to_transaction_wolgs()
            )
        except AlreadyExistError as e:
            raise AlreadyExistError(
                f"Transaction {transaction.trans_id} already exist",
                details="N/A" # don't pass database info
            )
        except FKNotExistError as e:
            raise FKNotExistError(
                f"User {user_id} does not exist",
                details="N/A" # don't pass database info
            )
            
        # add legs
        try:
            # convert legs to Leg objects
            legs = [
                Leg(
                    trans_id=transaction.trans_id,
                    user_id=user_id,
                    **leg.model_dump()
                ) for leg in transaction.legs
            ]
            await self.leg_repository.adds(legs)
        except AlreadyExistError as e:
            raise AlreadyExistError(
                f"Some legs already exist",
                details="N/A" # don't pass database info
            )
        except FKNotExistError as e:
            raise FKNotExistError(
                f"Some accounts or properties do not exist",
                details=str(e) # don't pass database info
            )

    @deserialize_cached_model(Transaction)
    @cached(
        cache=cache, 
        key_builder=lambda self, trans_id, user_id: f"transaction_{trans_id}_{user_id}", 
        ttl=int(timedelta(hours=24).total_seconds()),
        tags=['user_transactions']
    )
    async def get_transaction(self, trans_id: str, user_id: str) -> Transaction:
        try:
            transaction_wolgs = await self.transaction_body_repository.get(trans_id)
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        
        if transaction_wolgs.user_id != user_id:
            raise OpNotPermittedError(
                f"Transaction user ID {transaction_wolgs.user_id} must be the same as the user ID {user_id}",
                details=str(e) # don't pass database info
            )
            
        try:
            legs = await self.leg_repository.get_by_trans_id(trans_id)
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        return Transaction(
            trans_id=transaction_wolgs.trans_id,
            user_id=transaction_wolgs.user_id,
            trans_dt=transaction_wolgs.trans_dt,
            description=transaction_wolgs.description,
            legs=legs
        )
        
        
    async def remove_transaction(self, trans_id: str, user_id: str):
        # verify transaction exists and belongs to the user
        transaction_wolgs = await self.transaction_body_repository.get(trans_id)
        if transaction_wolgs.user_id != user_id:
            raise OpNotPermittedError(
                f"Transaction user ID {transaction_wolgs.user_id} must be the same as the user ID {user_id}",
                details=str(e) # don't pass database info
            )
        # remove legs first
        try:
            await self.leg_repository.remove_by_trans_id(trans_id)
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Transaction {trans_id} is associated with other data, cannot delete",
                details=str(e) # don't pass database info
            )
            
        try:
            await self.transaction_body_repository.remove(trans_id)
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Transaction {trans_id} is associated with other data, cannot delete",
                details=str(e) # don't pass database info
            )
            
        # Invalidate cache after successful update
        await cache.delete(f"transaction_{trans_id}_{user_id}")
            
    async def update_transaction(self, transaction: TransactionCreate, user_id: str):
        if transaction.user_id != user_id:
            raise OpNotPermittedError(
                f"Transaction user ID {transaction.user_id} must be the same as the user ID {user_id}",
                details="N/A" # don't pass database info
            )
            
        # get old leg ids first
        leg_ids = await self.leg_repository.get_leg_ids_by_trans_id(transaction.trans_id)
        
        # add new legs
        try:
            # convert legs to Leg objects
            legs = [
                Leg(
                    trans_id=transaction.trans_id,
                    user_id=user_id,
                    **leg.model_dump()
                ) for leg in transaction.legs
            ]
            await self.leg_repository.adds(legs)
        except AlreadyExistError as e:
            raise AlreadyExistError(
                f"Some legs already exist",
                details="N/A" # don't pass database info
            )
        except FKNotExistError as e:
            raise FKNotExistError(
                f"Some accounts or properties do not exist",
                details=str(e) # don't pass database info
            )
            
        # remove old legs only if new legs are added successfully
        
        try:
            await self.leg_repository.removes(leg_ids)
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {transaction.trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Transaction {transaction.trans_id} is associated with other data, cannot update",
                details=str(e) # don't pass database info
            )
        
        # finally update transaction body  
        try:
            await self.transaction_body_repository.update(transaction.to_transaction_wolgs())
        except NotExistError as e:
            raise NotExistError(
                f"Transaction {transaction.trans_id} does not exist",
                details="N/A" # don't pass database info
            )
        except FKNoDeleteUpdateError as e:
            raise FKNoDeleteUpdateError(
                f"Transaction {transaction.trans_id} is associated with other data, cannot update",
                details=str(e) # don't pass database info
            )
            
        # Invalidate cache after successful update
        await cache.delete(f"transaction_{transaction.trans_id}_{user_id}")