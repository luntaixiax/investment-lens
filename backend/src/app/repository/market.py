import logging
from typing import Dict, List
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, delete, select, insert, distinct
from sqlalchemy.exc import NoResultFound, IntegrityError
from src.app.repository.orm import FxORM
from src.app.model.market import FxRate
from src.app.model.enums import CurType
from src.app.model.exceptions import AlreadyExistError, FKNoDeleteUpdateError, NotExistError


class FxRepository:
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def add(self, fx_rate: FxRate):
        fx = FxORM(
            currency=fx_rate.currency,
            cur_dt=fx_rate.cur_dt,
            rate=fx_rate.rate
        )
        self.db_session.add(fx)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError(message=f"FX {fx_rate.currency} {fx_rate.cur_dt} already exist", details=str(e))
            

    async def adds(self, fx_rates: List[FxRate]):
        fxs = [FxORM(
            currency=fx_rate.currency,
            cur_dt=fx_rate.cur_dt,
            rate=fx_rate.rate
        ) for fx_rate in fx_rates]
        self.db_session.add_all(fxs)
        try:
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise AlreadyExistError("Some FX rates already exist", details=str(e))
            
    async def remove(self, currency: CurType, cur_dt: date):
        sql = delete(FxORM).where(FxORM.currency == currency, FxORM.cur_dt == cur_dt)
        
        try:
            await self.db_session.execute(sql)  
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
        
    async def remove_by_date(self, cur_dt: date):
        sql = delete(FxORM).where(FxORM.cur_dt == cur_dt)
        try:
            await self.db_session.execute(sql)
            await self.db_session.commit()
        except IntegrityError as e:
            await self.db_session.rollback()
            raise FKNoDeleteUpdateError(details=str(e))
            
    
    async def update(self, fx_rate: FxRate):
        sql = select(FxORM).where(FxORM.currency == fx_rate.currency, FxORM.cur_dt == fx_rate.cur_dt)
        try:
            result = await self.db_session.execute(sql)
            p = result.scalars().one()
        except NoResultFound as e:
            raise NotExistError(details=str(e))
        p.rate = fx_rate.rate
        self.db_session.add(p)
        await self.db_session.commit()

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
    
    async def get_hist_fx(self, currency: CurType, start_date: date, end_date: date) -> List[FxRate]:
        sql = select(FxORM).where(
            FxORM.currency == currency, 
            FxORM.cur_dt >= start_date, 
            FxORM.cur_dt <= end_date
        )
        result = await self.db_session.execute(sql)
        fxs = result.scalars().all()
        return [FxRate(currency=currency, cur_dt=fx.cur_dt, rate=fx.rate) for fx in fxs]
    
    async def find_missing_dates(self, start_date: date, end_date: date) -> List[date]:
        sql = select(
            distinct(FxORM.cur_dt).label('cur_dt')
        ).where(
            FxORM.currency.in_(CurType),
            FxORM.cur_dt >= start_date, 
            FxORM.cur_dt <= end_date
        )
        result = await self.db_session.execute(sql)
        available_dates = result.scalars().all()
        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        return [d for d in all_dates if d not in available_dates]