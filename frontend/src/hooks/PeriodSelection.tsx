import { useState, useMemo } from 'react';

export type TimePeriod = '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y';

/**
 * Calculates the start date based on a time period and end date
 * @param period - The time period (1W, 1M, 3M, 6M, 1Y, 5Y)
 * @param endDate - The end date to calculate from
 * @returns The calculated start date
 */
export function calculateStartDate(period: TimePeriod, endDate: Date): Date {
    switch (period) {
        case '1W':
            return new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
        case '1M':
            return new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
        case '3M':
            return new Date(endDate.getTime() - 90 * 24 * 60 * 60 * 1000);
        case '6M':
            return new Date(endDate.getTime() - 180 * 24 * 60 * 60 * 1000);
        case '1Y':
            return new Date(endDate.getTime() - 365 * 24 * 60 * 60 * 1000);
        case '5Y':
            return new Date(endDate.getTime() - 1825 * 24 * 60 * 60 * 1000);
        default:
            throw new Error(`Invalid period: ${period}`);
    }
}

export function usePeriodSelection(defaultPeriod: TimePeriod = '3M') {
    const [selectedPeriod, setSelectedPeriod] = useState<TimePeriod>(defaultPeriod);
    const periods: TimePeriod[] = ['1W', '1M', '3M', '6M', '1Y', '5Y'];

    const { startDate, endDate } = useMemo(() => {
        const today = new Date();
        const endDate = new Date(today);
        endDate.setDate(today.getDate() - 2); // current date - 2 days
        const startDate = calculateStartDate(selectedPeriod, endDate);
        return { startDate, endDate };
    }, [selectedPeriod]);

    return {
        selectedPeriod,
        setSelectedPeriod,
        periods,
        startDate,
        endDate,
    };
}

