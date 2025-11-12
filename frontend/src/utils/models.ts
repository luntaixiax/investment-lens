export type Currency = {
    symbol: string;
    id: number;
    flagClass: string;
}

export type PublicPropInfo = {
    symbol: string;
    name: string;
    exchange: string;
    currency: number;
    prop_type: number;
    industry: string;
    sector: string;
}

export type YFinancePricePoint = {
    dt: string;
    close: number;
    raw_close: number;
    adj_close: number;
    volume: number;
    stock_splits: number;
    dividends: number;
    split_factor: number;
}

export type FxRate = {
    cur_dt: string;
    rate: number;
}