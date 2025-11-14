import logging
from typing import Dict, List
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, delete, select, insert, distinct
from sqlmodel import Session, select, delete, distinct, case, func as f, and_, or_
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.app.model.enums import CurType
from src.app.model.registry import Property, PrivatePropOwnership
from src.app.repository.orm import PropertyORM, PrivatePropOwnershipORM
from src.app.model.exceptions import AlreadyExistError, FKNoDeleteUpdateError, NotExistError

class PropertyRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    def toPropertyORM(self, property: Property) -> PropertyORM:
        return PropertyORM(
            prop_id=property.prop_id,
            symbol=property.symbol,
            name=property.name,
            currency=property.currency,
            prop_type=property.prop_type,
            is_public=property.is_public,
            description=property.description
        )
        
    def fromPropertyORM(self, property_orm: PropertyORM) -> Property:
        return Property(
            prop_id=property_orm.prop_id,
            symbol=property_orm.symbol,
            name=property_orm.name,
            currency=property_orm.currency,
            prop_type=property_orm.prop_type,
            is_public=property_orm.is_public,
            description=property_orm.description
        )
        
    async def add(self, property: Property):
        property_orm = self.toPropertyORM(property)
        self.db_session.add(property_orm)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(details=str(e))
        
    async def remove(self, prop_id: str):
        sql = delete(PropertyORM).where(PropertyORM.prop_id == prop_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def update(self, property: Property):
        property_orm = self.toPropertyORM(property)
        
        sql = select(PropertyORM).where(PropertyORM.prop_id == property.prop_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        
        if not p == property_orm:
            p.symbol = property.symbol
            p.name = property.name
            p.currency = property.currency
            p.prop_type = property.prop_type
            p.is_public = property.is_public
            p.description = property.description
            
            self.db_session.add(p)
            await self.db_session.commit()
            await self.db_session.refresh(p) # update p to instantly have new values
        
    async def get(self, prop_id: str) -> Property:
        sql = select(PropertyORM).where(PropertyORM.prop_id == prop_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromPropertyORM(p)
        
    async def get_by_symbol(self, symbol: str) -> Property:
        sql = select(PropertyORM).where(PropertyORM.symbol == symbol)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromPropertyORM(p)
    
    async def gets(self, prop_ids: List[str]) -> List[Property]:
        sql = select(PropertyORM).where(PropertyORM.prop_id.in_(prop_ids))
        result = await self.db_session.execute(sql)
        return [self.fromPropertyORM(p) for p in result.scalars().all()]
    
    async def blurry_search_public(self, keyword: str, limit: int = 10) -> List[Property]:
        sql = (
            select(PropertyORM)
            .where(PropertyORM.is_public == True)
            .where(
                or_(
                    f.lower(PropertyORM.symbol).contains(keyword.lower()),
                    f.lower(PropertyORM.name).contains(keyword.lower()),
                    f.lower(PropertyORM.description).contains(keyword.lower())
                )
            )
            .limit(limit)
            .order_by(PropertyORM.symbol)
        )
        result = await self.db_session.execute(sql)
        return [self.fromPropertyORM(p) for p in result.scalars().all()]
    
class PrivatePropOwnershipRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    def toPrivatePropOwnershipORM(self, private_prop_ownership: PrivatePropOwnership) -> PrivatePropOwnershipORM:
        return PrivatePropOwnershipORM(
            ownership_id=private_prop_ownership.ownership_id,
            prop_id=private_prop_ownership.prop_id,
            user_id=private_prop_ownership.user_id
        )
        
    def fromPrivatePropOwnershipORM(self, private_prop_ownership_orm: PrivatePropOwnershipORM) -> PrivatePropOwnership:
        return PrivatePropOwnership(
            ownership_id=private_prop_ownership_orm.ownership_id,
            prop_id=private_prop_ownership_orm.prop_id,
            user_id=private_prop_ownership_orm.user_id
        )
        
    async def add(self, private_prop_ownership: PrivatePropOwnership):
        private_prop_ownership_orm = self.toPrivatePropOwnershipORM(private_prop_ownership)
        self.db_session.add(private_prop_ownership_orm)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(details=str(e))
        
    async def remove(self, ownership_id: str):
        sql = delete(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.ownership_id == ownership_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def remove_by_prop_id(self, prop_id: str):
        sql = delete(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.prop_id == prop_id)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def update(self, private_prop_ownership: PrivatePropOwnership):
        private_prop_ownership_orm = self.toPrivatePropOwnershipORM(private_prop_ownership)
        sql = select(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.ownership_id == private_prop_ownership.ownership_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        
        if not p == private_prop_ownership_orm:
            p.prop_id = private_prop_ownership.prop_id
            p.user_id = private_prop_ownership.user_id
            
            self.db_session.add(p)
            await self.db_session.commit()
            await self.db_session.refresh(p) # update p to instantly have new values
        
    async def get(self, ownership_id: str) -> PrivatePropOwnership:
        sql = select(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.ownership_id == ownership_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromPrivatePropOwnershipORM(p)
    
    async def get_by_prop_id(self, prop_id: str) -> PrivatePropOwnership:
        sql = select(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.prop_id == prop_id)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        return self.fromPrivatePropOwnershipORM(p)
    
    async def list_by_user(self, user_id: str) -> List[PrivatePropOwnership]:
        sql = select(PrivatePropOwnershipORM).where(PrivatePropOwnershipORM.user_id == user_id)
        result = await self.db_session.execute(sql)
        return [self.fromPrivatePropOwnershipORM(p) for p in result.scalars().all()]
        