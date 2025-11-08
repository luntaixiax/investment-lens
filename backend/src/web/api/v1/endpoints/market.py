from fastapi import APIRouter, Depends
from src.app.model.enums import CurType
from src.app.service.market import FxService
from src.web.dependency.service import get_fx_service
from datetime import date

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