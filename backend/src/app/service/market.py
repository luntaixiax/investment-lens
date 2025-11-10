import yfinance as yf
from currency_converter import CurrencyConverter, ECB_URL
import asyncio
from datetime import date, timedelta
from yokedcache import cached
import pandas as pd
from src.app.model.market import PublicPropInfo
from src.app.model.enums import CurType, PropertyType
from src.app.model.market import FxRate
from src.app.repository.market import FxRepository
from src.app.model.exceptions import NotExistError
from src.app.repository.cache import cache


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
    

FALL_BACK_CUR = {
    CurType.MOP : CurType.HKD
}
FALL_BACK_FX = {
    CurType.TWD: 33.5,
    CurType.CUP: 25.41
}
CURRENCY_CONVERTER = CurrencyConverter(
    currency_file = ECB_URL,
    fallback_on_missing_rate = True,
    fallback_on_missing_rate_method = 'linear_interpolation',
    fallback_on_wrong_date = True, 
    ref_currency = CurType.EUR.name # global base currency
)
CURRENCY_CONVERTER_CURRENCIES = CURRENCY_CONVERTER.currencies

class CurConverterWrapper:
    
    @classmethod
    def pull(cls, cur_dt: date, currency: CurType) -> FxRate:
        currencies = CURRENCY_CONVERTER_CURRENCIES
        if currency.name not in currencies: # type: ignore
            cur_fallback = FALL_BACK_CUR.get(currency)
            if cur_fallback is None:
                rate = FALL_BACK_FX.get(currency)
                if rate is None:
                    raise ValueError(f"No fallback rate found for currency {currency.name}")
                return FxRate(currency=currency, cur_dt=cur_dt, rate=rate)
        else:
            cur_fallback = currency
        
        rate = CURRENCY_CONVERTER.convert(
            amount = 100, 
            currency = CurType.EUR.name, # global base currency
            new_currency = cur_fallback.name, 
            date = cur_dt
        )
        return FxRate(currency=currency, cur_dt=cur_dt, rate=rate)
    
    @classmethod
    async def async_pull(cls, cur_dt: date, currency: CurType) -> FxRate:
        return await asyncio.to_thread(cls.pull, cur_dt, currency)
    
class FxService:
    
    def __init__(self, fx_repository: FxRepository):
        self.fx_repository = fx_repository
    
    @cached(
        cache=cache, 
        key_builder=lambda self, currency, cur_dt: f"fx_rate_{currency.name}_{cur_dt}", 
        ttl=int(timedelta(hours=1).total_seconds())
    )
    async def _get(self, currency: CurType, cur_dt: date) -> float:
        return await self.fx_repository.get(currency=currency, cur_dt=cur_dt)
    
    async def convert(self, amount: float, src_currency: CurType, tgt_currency: CurType, cur_dt: date) -> float:
        # convert from src_currency to base currency
        # Note: Cannot parallelize database queries on the same session (SQLAlchemy limitation)
        tgt_fx = await self._get(tgt_currency, cur_dt=cur_dt)
        src_fx = await self._get(src_currency, cur_dt=cur_dt)
        return amount * tgt_fx / src_fx
    
    async def get_hist_fx(self, currency: CurType, start_date: date, end_date: date) -> list[FxRate]:
        return await self.fx_repository.get_hist_fx(currency=currency, start_date=start_date, end_date=end_date)
    
    async def download_fx_rates(self, cur_dt: date):
        fx_rates = await asyncio.gather(*[CurConverterWrapper.async_pull(cur_dt, cur) for cur in CurType])
        await self.fx_repository.remove_by_date(cur_dt) # remove all existing fx rates for the date
        await self.fx_repository.adds(fx_rates)

    async def download_missing_fx_rates(self, start_date: date, end_date: date):
        missing_dates = await self.fx_repository.find_missing_dates(start_date, end_date)
        fx_rates = await asyncio.gather(*[CurConverterWrapper.async_pull(cur_dt, cur) for cur_dt in missing_dates for cur in CurType])
        await self.fx_repository.adds(fx_rates)