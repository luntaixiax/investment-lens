from datetime import date
from fastapi import APIRouter, Depends
from src.app.model.enums import CurType
from src.app.service.market import FxService
from src.web.dependency.service import get_fx_service, get_yfinance_service
from src.app.model.market import FxRate, FxPoint, PublicPropInfo, YFinancePricePoint
from src.web.dependency.auth import get_admin_user
from src.app.model.user import User
from src.app.service.market import YFinanceService

router = APIRouter(
    prefix="/market",
    tags=["market"],
)

@router.get("/fx/get_rate")
async def get_fx_rate(
    src_currency: CurType, 
    tgt_currency: CurType, 
    cur_dt: date,
    fx_service: FxService = Depends(get_fx_service)
) -> float:
    return await fx_service.convert(1.0, src_currency, tgt_currency, cur_dt)


@router.get("/fx/get_hist_fx")
async def get_hist_fx(
    currency: CurType,
    start_date: date,
    end_date: date,
    fx_service: FxService = Depends(get_fx_service)
) -> list[FxRate]:
    return await fx_service.get_hist_fx(currency=currency, start_date=start_date, end_date=end_date)

@router.get("/fx/get_hist_fx_points")
async def get_hist_fx_points(
    src_currency: CurType,
    tgt_currency: CurType,
    start_date: date,
    end_date: date,
    fx_service: FxService = Depends(get_fx_service)
) -> list[FxPoint]:
    return await fx_service.get_hist_fx_points(
        src_currency=src_currency, tgt_currency=tgt_currency, start_date=start_date, end_date=end_date
    )


@router.post("/fx/download_fx_rates")
async def download_fx_rates(
    cur_dt: date,
    fx_service: FxService = Depends(get_fx_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await fx_service.download_fx_rates(cur_dt)
    
@router.post("/fx/download_missing_fx_rates")
async def download_missing_fx_rates(
    start_date: date,
    end_date: date,
    fx_service: FxService = Depends(get_fx_service),
    admin_user: User = Depends(get_admin_user)
) -> None:
    await fx_service.download_missing_fx_rates(start_date, end_date)
    
    
@router.get("/yfinance/exists")
async def yfinance_exists(
    symbol: str,
    yfinance_service: YFinanceService = Depends(get_yfinance_service)
) -> bool:
    return await yfinance_service.exists(symbol)

@router.get("/yfinance/get_public_prop_info")
async def yfinance_get_public_prop_info(
    symbol: str,
    yfinance_service: YFinanceService = Depends(get_yfinance_service)
) -> PublicPropInfo:
    return await yfinance_service.get_public_prop_info(symbol)

@router.get("/yfinance/get_hist_data")
async def yfinance_get_hist_data(
    symbol: str,
    start_date: date,
    end_date: date,
    yfinance_service: YFinanceService = Depends(get_yfinance_service)
) -> list[YFinancePricePoint]:
    return await yfinance_service.get_hist_data(symbol, start_date, end_date)