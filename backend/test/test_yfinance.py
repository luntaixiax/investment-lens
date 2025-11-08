import yfinance as yf
from datetime import date
import pandas as pd
import pytest
from src.app.model.enums import CurType, PropertyType
from src.app.service.market import YFinanceWrapper
pd.set_option('display.max_columns', None)

@pytest.mark.parametrize("symbol", ["INVALID"])
def test_yfinance_invalid(symbol):
    """Test that invalid symbols do not exist."""
    from src.app.service.market import YFinanceWrapper
    
    yfw = YFinanceWrapper(symbol)
    assert not yfw.exists()


@pytest.mark.parametrize("symbol,expected_currency,expected_prop_type", [
    ("AAPL", CurType.USD, PropertyType.STOCK),
    ("FIE.TO", CurType.CAD, PropertyType.ETF),
    ("0P0001NY10.TO", CurType.CAD, PropertyType.FUND_PUB),
    ("USDC-USD", CurType.USD, PropertyType.CRYPTO),
    ("CL=F", CurType.USD, PropertyType.DERIVATIVE),
])
def test_yfinance_info_and_hist_data(symbol: str, expected_currency: CurType, expected_prop_type: PropertyType):
    """Test that valid symbols exist and have correct currency and property type."""
    
    yfw = YFinanceWrapper(symbol)
    assert yfw.exists()
    
    info = yfw.get_public_prop_info()
    assert info.currency == expected_currency
    assert info.prop_type == expected_prop_type
    
    df = yfw.get_hist_data(date(2024, 1, 1), date(2024, 12, 31))
    assert not df.empty
    assert df.index.min().to_pydatetime().date() == date(2024, 1, 1)
    assert df.index.max().to_pydatetime().date() == date(2024, 12, 31)
    assert len(df) == 366
    assert set(df.columns.tolist()) == set(['open', 'high', 'low', 'close', 'adj_close', 'volume', 'stock_splits', 'dividends', 'split_factor'])
    
