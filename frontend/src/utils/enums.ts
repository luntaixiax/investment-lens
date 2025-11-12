import type { Currency } from "./models";

export const CURRENCY_ENUMS: Record<string, number> = {
    USD: 1,
    CAD: 2,
    CNY: 3,
    GBP: 4,
    AUD: 5,
    JPY: 6,
    EUR: 7,
    MOP: 8,
    HKD: 9,
    CHF: 10,
    TWD: 11,
    THB: 12,
    MXN: 13,
    CUP: 14,
    RUB: 15,
}

export const CURRENCIES: Currency[] = [
    { symbol: 'USD', id: CURRENCY_ENUMS.USD, flagClass: 'fi-us' },
    { symbol: 'CAD', id: CURRENCY_ENUMS.CAD, flagClass: 'fi-ca' },
    { symbol: 'CNY', id: CURRENCY_ENUMS.CNY, flagClass: 'fi-cn' },
    { symbol: 'GBP', id: CURRENCY_ENUMS.GBP, flagClass: 'fi-gb' },
    { symbol: 'AUD', id: CURRENCY_ENUMS.AUD, flagClass: 'fi-au' },
    { symbol: 'JPY', id: CURRENCY_ENUMS.JPY, flagClass: 'fi-jp' },
    { symbol: 'EUR', id: CURRENCY_ENUMS.EUR, flagClass: 'fi-eu' },
    { symbol: 'MOP', id: CURRENCY_ENUMS.MOP, flagClass: 'fi-mo' },
    { symbol: 'HKD', id: CURRENCY_ENUMS.HKD, flagClass: 'fi-hk' },
    { symbol: 'CHF', id: CURRENCY_ENUMS.CHF, flagClass: 'fi-ch' },
    { symbol: 'TWD', id: CURRENCY_ENUMS.TWD, flagClass: 'fi-tw' },
    { symbol: 'THB', id: CURRENCY_ENUMS.THB, flagClass: 'fi-th' },
    { symbol: 'MXN', id: CURRENCY_ENUMS.MXN, flagClass: 'fi-mx' },
    { symbol: 'CUP', id: CURRENCY_ENUMS.CUP, flagClass: 'fi-cu' },
    { symbol: 'RUB', id: CURRENCY_ENUMS.RUB, flagClass: 'fi-ru' },
]

export const PROPERTY_ENUMS: Record<string, number> = {
    CASH: 0,
    MONEY_MARKET: 1,
    BOND: 2,
    STOCK: 3,
    ETF: 4,
    FUND_PUB: 5,
    FUND_PRIV: 6,
    DERIVATIVE: 7,
    REAL_ESTATE: 8,
    CRYPTO: 9,
    DEBT: 10,
    OTHER: 11,
}

export function getPropTypeByValue(value: number): string | undefined {
    return Object.keys(PROPERTY_ENUMS).find((key) => PROPERTY_ENUMS[key] === value);
}
  