from enum import IntEnum, unique

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
    BOMD = 2
    STOCK = 3
    ETF = 4
    FUND = 5
    DERIVATIVE = 6
    REAL_ESTATE = 7
    CRYPTO = 8
    DEBT = 9 # personal debt
    OTHER = 10
    
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