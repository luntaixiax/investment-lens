import { useEffect, useState } from 'react';
import axios from 'axios';
import { CURRENCIES, type Currency } from '../components/CurrencyDropdown';
import { type FxRate } from '../components/CurrencyChart';

export type TimePeriod = '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y';

export function useCurrencyData() {
    const [fromCurrency, setFromCurrency] = useState<Currency>(CURRENCIES[0]);
    const [toCurrency, setToCurrency] = useState<Currency>(CURRENCIES[1]);
    const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>('3M');

    // historical fx rates for given pair of currencies
    const [fxRates, setFxRates] = useState<FxRate[]>([]);
    // current fx rate for given pair of currencies
    const [currentFxRate, setCurrentFxRate] = useState<number>(1.0);

    const periods: TimePeriod[] = ['1W', '1M', '3M', '6M', '1Y', '5Y'];

    useEffect(() => {
        async function fetchFxRates(startDate: Date, endDate: Date) {
            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = endDate.toISOString().split('T')[0];

            const [fxRates, currentFxRate] = await Promise.all([
                axios.get(`/backend/api/v1/market/fx/get_hist_fx_points?src_currency=${fromCurrency.id}&tgt_currency=${toCurrency.id}&start_date=${startDateStr}&end_date=${endDateStr}`),
                axios.get(`/backend/api/v1/market/fx/get_rate?src_currency=${fromCurrency.id}&tgt_currency=${toCurrency.id}&cur_dt=${endDateStr}`)
            ]);
            setFxRates(fxRates.data);
            setCurrentFxRate(currentFxRate.data);
        }

        let startDate: Date;
        let endDate: Date;
        endDate = new Date(2025, 10, 10);

        switch (selectedPeriod) {
            case '1W':
                startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case '1M':
                startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            case '3M':
                startDate = new Date(endDate.getTime() - 90 * 24 * 60 * 60 * 1000);
                break;
            case '6M':
                startDate = new Date(endDate.getTime() - 180 * 24 * 60 * 60 * 1000);
                break;
            case '1Y':
                startDate = new Date(endDate.getTime() - 365 * 24 * 60 * 60 * 1000);
                break;
            case '5Y':
                startDate = new Date(endDate.getTime() - 1825 * 24 * 60 * 60 * 1000);
                break;
            default:
                throw new Error(`Invalid period: ${selectedPeriod}`);
        }

        fetchFxRates(startDate, endDate).catch(error => {
            console.error('Error fetching market data:', error);
        });
    }, [fromCurrency, toCurrency, selectedPeriod]);

    return {
        fromCurrency,
        setFromCurrency,
        toCurrency,
        setToCurrency,
        selectedPeriod,
        setSelectedPeriod,
        fxRates,
        currentFxRate,
        periods,
    };
}

