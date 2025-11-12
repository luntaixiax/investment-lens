import { useEffect, useState } from 'react';
import axios from 'axios';
import { CURRENCIES } from '../utils/enums';
import type { Currency, FxRate } from '../utils/models';

export function useCurrencyData(startDate: Date, endDate: Date) {
    const [fromCurrency, setFromCurrency] = useState<Currency>(CURRENCIES[0]);
    const [toCurrency, setToCurrency] = useState<Currency>(CURRENCIES[1]);

    // historical fx rates for given pair of currencies
    const [fxRates, setFxRates] = useState<FxRate[]>([]);
    // current fx rate for given pair of currencies
    const [currentFxRate, setCurrentFxRate] = useState<number>(1.0);

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

        fetchFxRates(startDate, endDate).catch(error => {
            console.error('Error fetching market data:', error);
        });
    }, [fromCurrency, toCurrency, startDate, endDate]);

    return {
        fromCurrency,
        setFromCurrency,
        toCurrency,
        setToCurrency,
        fxRates,
        currentFxRate,
    };
}

