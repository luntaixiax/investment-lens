import yfinance as yf
from currency_converter import CurrencyConverter, ECB_URL
import asyncio
from datetime import date, timedelta
import pandas as pd
from src.app.model.market import PublicPropInfo
from src.app.model.enums import CurType, PropertyType
from src.app.repository.market import FxRepository
from src.app.model.exceptions import NotExistError

class YFinanceWrapper:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.yf_ticker = yf.Ticker(self.symbol)
        
    def exists(self) -> bool:
        try:
            self.yf_ticker.get_info()['currency']
        except KeyError:
            return False
        return True
        
    def get_public_prop_info(self) -> PublicPropInfo:
        
        info = self.yf_ticker.get_info()
        quote_type = info.get('quoteType')
        if quote_type == 'MUTUALFUND':
            prop_type = PropertyType.FUND_PUB
        elif quote_type == 'ETF':
            prop_type = PropertyType.ETF
        elif quote_type == 'CRYPTOCURRENCY':
            prop_type = PropertyType.CRYPTO
        elif quote_type == 'EQUITY':
            prop_type = PropertyType.STOCK
        elif quote_type == 'FUTURE':
            prop_type = PropertyType.DERIVATIVE
        elif quote_type == 'CRYPTOCURRENCY':
            prop_type = PropertyType.CRYPTO
        else:
            prop_type = PropertyType.OTHER

        return PublicPropInfo(
            symbol=self.symbol,
            name=info.get('longName'),
            exchange=info.get('exchange'),
            currency=CurType[info['currency']],
            prop_type=prop_type,
            industry=info.get('industry'),
            sector=info.get('sector'),
            country=info.get('country'),
            website=info.get('website'),
            description=info.get('longBusinessSummary'),
        )
        
    
    def get_hist_data(self, start_date: date, end_date: date) -> pd.DataFrame:
        df = self.yf_ticker.history(
            start=start_date-timedelta(days=10), # to avoid holiday at beginning 
            end=end_date+timedelta(days=10), # to avoid holiday at end
            interval="1d", 
            auto_adjust=False
        )
        # these are prices adjusted for splits only
        df = df.rename(columns={
            'Open': 'open', 
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close',
            'Adj Close': 'adj_close', # historical prices adjusted for splits and dividends
            'Volume': 'volume', 
            'Stock Splits': 'stock_splits', 
            'Dividends': 'dividends'
        })
        df.index = df.index.date
        # ffill non-trading days values
        all_days = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        df = df.reindex(all_days)
        # stock splits and dividends are 0 for non-trading days
        df[['stock_splits', 'dividends']] = df[['stock_splits', 'dividends']].fillna(0)
        df = df.ffill() # other days values are filled with previous day values
        
        df['split_factor'] = df['stock_splits'].replace(0.0, 1.0)[::-1].cumprod()[::-1]
        
        # these are raw prices, not adjusted for splits and dividends
        # df['raw_close'] = df["close"] * df['split_factor']
        # df['raw_open'] = df["open"] * df['split_factor']
        # df['raw_high'] = df["high"] * df['split_factor']
        # df['raw_low'] = df["low"] * df['split_factor']
        
        # filter out days outside the range
        df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
        return df[['open', 'high', 'low', 'close', 'adj_close', 'volume', 'stock_splits', 'dividends', 'split_factor']]
    
    
class FxService:
    GLOBAL_BASE_CUR = CurType.EUR
    FALL_BACK_CUR = {
        CurType.MOP : CurType.HKD
    }
    FALL_BACK_FX = {
        CurType.TWD: 33.5,
        CurType.CUP: 25.41
    }
    
    def __init__(self, fx_repository: FxRepository):
        self.fx_repository = fx_repository
        self.currency_converter = CurrencyConverter(
            currency_file = ECB_URL,
            fallback_on_missing_rate = True,
            fallback_on_missing_rate_method = 'last_known',
            fallback_on_wrong_date = True, 
            ref_currency = self.GLOBAL_BASE_CUR.name
        )
            
    async def pull(self, cur_dt: date, overwrite: bool = False):
        # fresh new run -- pull all at one time
        existing_fxs = await self.fx_repository.get_fx_on_date(cur_dt=cur_dt)
        existing_fxs = list(existing_fxs.keys())
        if len(existing_fxs) == 0:
            rates = await self._pull(curs = CurType, cur_dt = cur_dt) # type: ignore
            await self.fx_repository.adds(
                currencies=[cur for cur in CurType],
                cur_dt=cur_dt,
                rates=rates
            )
            return
        
        if overwrite:
            rates = await self._pull(curs = CurType, cur_dt = cur_dt) # type: ignore
            # Batch update/adds in a single transaction (more efficient than parallel commits)
            await self.fx_repository.updates_or_adds(
                currencies=[cur for cur in CurType],
                cur_dt=cur_dt,
                rates=rates,
                existing_currencies=existing_fxs
            )
        else:
            # have at least some existing values
            missing_fxs = [cur for cur in CurType if cur not in existing_fxs]
            rates = await self._pull(curs = missing_fxs, cur_dt = cur_dt)
            # Batch add in a single transaction (more efficient than parallel commits)
            await self.fx_repository.adds(
                currencies=missing_fxs,
                cur_dt=cur_dt,
                rates=rates
            )   
            
    async def _pull(self, curs: list[CurType], cur_dt: date) -> list[float]:
        # pull fx rates at given date
        
        # for 100 base currency, how much local currency is it
        currencies = self.currency_converter.currencies
        
        async def _pull_single_currency(cur: CurType) -> float:
            """Pull rate for a single currency."""
            if cur.name not in currencies: # type: ignore
                cur_fallback = self.FALL_BACK_CUR.get(cur)
                if cur_fallback is None:
                    rate = self.FALL_BACK_FX.get(cur)
                    if rate is None:
                        raise ValueError(f"No fallback rate found for currency {cur.name}")
                    return rate
            else:
                cur_fallback = cur
            
            rate = await asyncio.to_thread(
                self.currency_converter.convert, # type: ignore  # IO bounded operation
                amount = 100, 
                currency = self.GLOBAL_BASE_CUR.name, 
                new_currency = cur_fallback.name, 
                date = cur_dt
            )
            return round(rate, 4)
        
        # Parallelize all currency conversions
        rates = await asyncio.gather(*[_pull_single_currency(cur) for cur in curs])
        return list(rates)
        
    async def _get(self, currency: CurType, cur_dt: date) -> float:
        try:
            rate = await self.fx_repository.get(currency=currency, cur_dt=cur_dt)
        except NotExistError:
            await self.pull(cur_dt=cur_dt, overwrite=False)
            return await self.fx_repository.get(currency=currency, cur_dt=cur_dt)
        else:
            return rate
    
    async def convert(self, amount: float, src_currency: CurType, tgt_currency: CurType, cur_dt: date) -> float:
        # convert from src_currency to base currency
        # Note: Cannot parallelize database queries on the same session (SQLAlchemy limitation)
        tgt_fx = await self._get(tgt_currency, cur_dt=cur_dt)
        src_fx = await self._get(src_currency, cur_dt=cur_dt)
        return amount * tgt_fx / src_fx