import logging
from typing import Dict, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, delete, select
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.app.repository.orm import FxORM
from src.app.model.enums import CurType
from src.app.model.exceptions import AlreadyExistError, FKNoDeleteUpdateError, NotExistError


class FxRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def add(self, currency: CurType, cur_dt: date, rate: float):
        fx = FxORM(
            currency=currency,
            cur_dt=cur_dt,
            rate=rate
        )
        self.db_session.add(fx)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(message=f"FX {currency} {cur_dt} already exist", details=str(e))
            

    async def adds(self, currencies: List[CurType], cur_dt: date, rates: List[float]):
        for currency, rate in zip(currencies, rates):
            fx = FxORM(
                currency=currency,
                cur_dt=cur_dt,
                rate=rate
            )
            self.db_session.add(fx)
        
        # commit in one load
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(message=f"FX {currency} {cur_dt} already exist", details=str(e))
            
    async def remove(self, currency: CurType, cur_dt: date):
        sql = delete(FxORM).where(FxORM.currency == currency, FxORM.cur_dt == cur_dt)
        
        try:
            await self.db_session.execute(sql)  
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
            
    
    async def update(self, currency: CurType, cur_dt: date, rate: float):
        sql = select(FxORM).where(FxORM.currency == currency, FxORM.cur_dt == cur_dt)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound:
            raise NotExistError(f"FX not exist, currency = {currency}, cur_dt = {cur_dt}")
        
        # update
        p.rate = rate
        
        self.db_session.add(p)
        await self.db_session.commit()
        await self.db_session.refresh(p) # update p to instantly have new values
    
    async def updates_or_adds(self, currencies: List[CurType], cur_dt: date, rates: List[float], existing_currencies: List[CurType]):
        """Batch update existing currencies and add new ones in a single transaction."""
        existing_set = set(existing_currencies)
        
        # Fetch all existing records in one query
        if existing_set:
            sql = select(FxORM).where(
                FxORM.cur_dt == cur_dt,
                FxORM.currency.in_(existing_set)
            )
            result = await self.db_session.execute(sql)
            existing_records = {record.currency: record for record in result.scalars().all()}
        else:
            existing_records = {}
        
        # Update existing or add new
        for currency, rate in zip(currencies, rates):
            if currency in existing_records:
                # Update existing
                existing_records[currency].rate = rate
                self.db_session.add(existing_records[currency])
            else:
                # Add new
                fx = FxORM(currency=currency, cur_dt=cur_dt, rate=rate)
                self.db_session.add(fx)
        
        # Commit all changes in one transaction
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            currency_msg = currencies[0] if currencies else "unknown"
            raise AlreadyExistError(message=f"FX {currency_msg} {cur_dt} already exist", details=str(e))

    async def get(self, currency: CurType, cur_dt: date) -> float:
        sql = select(FxORM.rate).where(FxORM.currency == currency, FxORM.cur_dt == cur_dt)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one() # get the fx
        except NoResultFound:
            raise NotExistError(f"FX not exist, currency = {currency}, cur_dt = {cur_dt}")
        return p
    
    async def get_fx_on_date(self, cur_dt: date) -> Dict[CurType, float]:
        sql = select(FxORM.currency, FxORM.rate).where(FxORM.cur_dt == cur_dt)
        result = await self.db_session.execute(sql)
        fxs = result.scalars().all() # get the fx
        
        # .all() never raises NoResultFound, it returns empty list
        return {CurType(fx.currency): fx.rate for fx in fxs}