from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select, insert
from sqlalchemy.exc import IntegrityError, NoResultFound
from src.app.repository.orm import TransactionORM, LegORM
from src.app.model.transaction import TransactionWOLegs, Leg
from src.app.model.exceptions import NotExistError
from src.app.repository.orm import infer_integrity_error

class TransactionBodyRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    def toTransactionORM(self, transaction: TransactionWOLegs) -> TransactionORM:
        return TransactionORM(
            trans_id=transaction.trans_id,
            user_id=transaction.user_id,
            trans_dt=transaction.trans_dt,
            description=transaction.description
        )
        
    def fromTransactionORM(self, transaction_orm: TransactionORM) -> TransactionWOLegs:
        return TransactionWOLegs(
            trans_id=transaction_orm.trans_id,
            user_id=transaction_orm.user_id,
            trans_dt=transaction_orm.trans_dt,
            description=transaction_orm.description
        )
        
    async def add(self, transaction: TransactionWOLegs):
        transaction_orm = self.toTransactionORM(transaction)    # type: ignore
        self.db_session.add(transaction_orm)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=True)
        
    async def remove(self, trans_id: str):
        sql = delete(TransactionORM).where(TransactionORM.trans_id == trans_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=False)
        
    async def update(self, transaction: TransactionWOLegs):
        transaction_orm = self.toTransactionORM(transaction)    # type: ignore
        sql = select(TransactionORM).where(TransactionORM.trans_id == transaction.trans_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        if not p == transaction_orm:
            p.trans_dt = transaction.trans_dt
            p.description = transaction.description
            p.user_id = transaction.user_id
            self.db_session.add(p)
            await self.db_session.commit()
            await self.db_session.refresh(p) # update p to instantly have new values
        
    async def get(self, trans_id: str) -> TransactionWOLegs:
        sql = select(TransactionORM).where(TransactionORM.trans_id == trans_id)
        result = await self.db_session.execute(sql)
        try:
            transaction_orm = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromTransactionORM(transaction_orm)
    
    
class LegRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    def toLegORM(self, leg: Leg) -> LegORM:
        return LegORM(
            leg_id=leg.leg_id,
            trans_id=leg.trans_id,
            user_id=leg.user_id,
            leg_type=leg.leg_type,
            acct_id=leg.acct_id,
            prop_id=leg.prop_id,
            quantity=leg.quantity,
            price=leg.price
        )
        
    def fromLegORM(self, leg_orm: LegORM) -> Leg:
        return Leg(
            leg_id=leg_orm.leg_id,
            trans_id=leg_orm.trans_id,
            user_id=leg_orm.user_id,
            leg_type=leg_orm.leg_type,
            acct_id=leg_orm.acct_id,
            prop_id=leg_orm.prop_id,
            quantity=leg_orm.quantity,
            price=leg_orm.price
        )
        
    async def add(self, leg: Leg):
        leg_orm = self.toLegORM(leg)    # type: ignore
        self.db_session.add(leg_orm)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=True)
        
    async def adds(self, legs: list[Leg]):
        leg_orms = [self.toLegORM(leg) for leg in legs]    # type: ignore
        self.db_session.add_all(leg_orms)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=True)
        
    async def remove(self, leg_id: str):
        sql = delete(LegORM).where(LegORM.leg_id == leg_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=False)
        
    async def remove_by_trans_id(self, trans_id: str):
        sql = delete(LegORM).where(LegORM.trans_id == trans_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=False)
        
    async def removes(self, leg_ids: list[str]):
        sql = delete(LegORM).where(LegORM.leg_id.in_(leg_ids))
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise infer_integrity_error(e, during_creation=False)
        
        
    async def update(self, leg: Leg):
        leg_orm = self.toLegORM(leg)    # type: ignore
        sql = select(LegORM).where(LegORM.leg_id == leg.leg_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        if not p == leg_orm:
            p.trans_id = leg.trans_id
            p.user_id = leg.user_id
            p.leg_type = leg.leg_type
            p.acct_id = leg.acct_id
            p.prop_id = leg.prop_id
            p.quantity = leg.quantity
            p.price = leg.price
            
            self.db_session.add(p)
            await self.db_session.commit()
            await self.db_session.refresh(p) # update p to instantly have new values
            
    async def get(self, leg_id: str) -> Leg:
        sql = select(LegORM).where(LegORM.leg_id == leg_id)
        result = await self.db_session.execute(sql)
        try:
            leg_orm = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromLegORM(leg_orm)
    
    async def get_by_trans_id(self, trans_id: str) -> list[Leg]:
        sql = select(LegORM).where(LegORM.trans_id == trans_id)
        result = await self.db_session.execute(sql)
        return [self.fromLegORM(p) for p in result.scalars().all()]
    
    async def get_leg_ids_by_trans_id(self, trans_id: str) -> list[str]:
        sql = select(LegORM.leg_id).where(LegORM.trans_id == trans_id)
        result = await self.db_session.execute(sql)
        return result.scalars().all()