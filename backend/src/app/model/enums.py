from enum import IntEnum, Enum, unique

@unique
class CurType(IntEnum):
    USD = 1
    CAD = 2
    CNY = 3
    GBP = 4
    AUD = 5
    JPY = 6
    EUR = 7
    MOP = 8
    HKD = 9
    CHF = 10
    TWD = 11
    THB = 12
    MXN = 13
    CUP = 14
    RUB = 15
    
@unique
class PropertyType(IntEnum):
    CASH = 0
    MONEY_MARKET = 1
    BOND = 2
    STOCK = 3
    ETF = 4 # self-trading funds
    FUND_PUB = 5 # mutual funds
    FUND_PRIV = 6 # private funds
    DERIVATIVE = 7
    REAL_ESTATE = 8
    CRYPTO = 9
    DEBT = 10 # personal debt
    BUSINESS = 11 # business (company, franchise, etc.)
    OTHER = 12
    
@unique
class PlanType(IntEnum):
    PERS = 0
    CORP = 1
    RRSP = 2
    TFSA = 3
    RRIF = 4
    LIRA = 5
    LIF = 6
    LP = 7
    OTHER = 8

@unique
class TransactionType(IntEnum):
    DEPOSIT = 0
    WITHDRAWAL = 1
    BUY = 2
    SELL = 3
    FEE = 4
    INTEREST = 5
    DIVIDEND = 6
    TAX = 7
    OTHER = 8
    
    
@unique
class EstateType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    LOT = "lot"
    OTHER = "other"
    
@unique
class BusinessType(str, Enum):
    CORPORATION = "corporation"
    SMALL_BUSINESS = "small business"
    FRANCHISE = "franchise"
    SOLE_PROPRIETORSHIP = "sole proprietorship"
    PARTNERSHIP = "partnership"
    OTHER = "other"
    
@unique
class UnderlyingType(str, Enum):
    EQUITY = "equity"
    DEBT = "debt"
    COMMODITY = "commodity"
    REAL_ESTATE = "real property"
    PROJECT = "project"
    HYBRID = "hybrid"
    OTHER = "other"
    
@unique
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    
@unique
class LiquidityType(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"