import yfinance as yf
from currency_converter import CurrencyConverter, ECB_URL
import asyncio
from datetime import date, timedelta
from yokedcache import cached
import pandas as pd
from src.app.model.market import PublicPropInfo
from src.app.model.registry import Property
from src.app.model.enums import CurType, PropertyType
from src.app.model.market import FxRate, FxPoint, YFinancePricePoint
from src.app.repository.market import FxRepository
from src.app.model.exceptions import NotExistError
from src.app.repository.cache import cache
from src.app.service.registry import RegistryService


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
        
        try:
        
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
            
        except Exception as e:
            raise NotExistError(f"Error getting public property info for symbol {self.symbol}")
        
    
    def get_hist_data(self, start_date: date, end_date: date) -> pd.DataFrame:
        try:
            df = self.yf_ticker.history(
                start=start_date-timedelta(days=10), # to avoid holiday at beginning
                # make sure split factor is calculated correctly
                end=date.today(), 
                interval="1d", 
                auto_adjust=False
            )
        except Exception as e:
            raise NotExistError(f"Error getting historical data for symbol {self.symbol}")
        
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
        
        # filter out days outside the range
        df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]
        return df[['open', 'high', 'low', 'close', 'adj_close', 'volume', 'stock_splits', 'dividends', 'split_factor']]


class YFinanceService:
    
    def __init__(self, registry_service: RegistryService):
        self.registry_service = registry_service
        
    @cached(
        cache=cache, 
        key_builder=lambda self, symbol: f"yfinance_exists_{symbol}", 
        ttl=int(timedelta(hours=24).total_seconds())
    )
    async def exists(self, symbol: str) -> bool:
        return await asyncio.to_thread(YFinanceWrapper(symbol).exists)
    
    @cached(
        cache=cache, 
        key_builder=lambda self, symbol: f"yfinance_public_prop_info_{symbol}", 
        ttl=int(timedelta(hours=24).total_seconds())
    )
    async def _get_public_prop_info_cached(self, symbol: str):
        return await asyncio.to_thread(YFinanceWrapper(symbol).get_public_prop_info)
    
    async def get_public_prop_info(self, symbol: str) -> PublicPropInfo:
        result = await self._get_public_prop_info_cached(symbol)
        # If result comes from cache, it may be a dict instead of PublicPropInfo
        if isinstance(result, dict):
            return PublicPropInfo.model_validate(result)
        return result
    
    async def get_hist_data(self, symbol: str, start_date: date, end_date: date) -> list[YFinancePricePoint]:
        df = await asyncio.to_thread(YFinanceWrapper(symbol).get_hist_data, start_date, end_date)
        return [
            YFinancePricePoint(
                dt=dt.to_pydatetime().date(), 
                close=rows.close, 
                adj_close=rows.adj_close, 
                volume=rows.volume, 
                stock_splits=rows.stock_splits, 
                dividends=rows.dividends, 
                split_factor=rows.split_factor
            ) for dt, rows in df.iterrows()
        ] if not df.empty else []
        
    async def register(self, symbol: str):
        if not await self.exists(symbol):
            raise NotExistError(f"Symbol {symbol} does not exist")
        public_prop_info = await self.get_public_prop_info(symbol)
        
        property = Property(
            symbol=public_prop_info.symbol,
            name=public_prop_info.name,
            currency=public_prop_info.currency,
            prop_type=public_prop_info.prop_type,
            is_public=True,
            description=public_prop_info.description
        )
        await self.registry_service.register_public_property(property)
        

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
    
    async def get_hist_fx_points(self, src_currency: CurType, tgt_currency: CurType, start_date: date, end_date: date) -> list[FxPoint]:
        src_hist = await self.get_hist_fx(currency=src_currency, start_date=start_date, end_date=end_date)
        tgt_hist = await self.get_hist_fx(currency=tgt_currency, start_date=start_date, end_date=end_date)
        return [FxPoint(cur_dt=src_hist.cur_dt, rate=tgt_hist.rate / src_hist.rate) for src_hist, tgt_hist in zip(src_hist, tgt_hist)]
    
    async def download_fx_rates(self, cur_dt: date):
        fx_rates = await asyncio.gather(*[CurConverterWrapper.async_pull(cur_dt, cur) for cur in CurType])
        await self.fx_repository.remove_by_date(cur_dt) # remove all existing fx rates for the date
        await self.fx_repository.adds(fx_rates)

    async def download_missing_fx_rates(self, start_date: date, end_date: date):
        missing_dates = await self.fx_repository.find_missing_dates(start_date, end_date)
        fx_rates = await asyncio.gather(
            *[CurConverterWrapper.async_pull(cur_dt, cur) 
            for cur_dt in missing_dates for cur in CurType]
        )
        await self.fx_repository.adds(fx_rates)