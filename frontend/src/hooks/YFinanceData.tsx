import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import type { PublicPropInfo } from '../utils/models';
import type { YFinancePricePoint } from '../utils/models';
import { useClickOutside } from './ClickOutSide';

export function useYFinanceData(startDate: Date, endDate: Date) {
    // symbol when user is typing in the search bar
    const [symbol, setSymbol] = useState<string>('');
    // whether the search bar is focused
    const [isFocused, setIsFocused] = useState<boolean>(false);
    
    // public property information
    const [publicPropInfo, setPublicPropInfo] = useState<PublicPropInfo | null>(null);

    // only set when user click the search board item
    const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
    // historical data for the selected symbol
    const [histData, setHistData] = useState<YFinancePricePoint[]>([]);
    // whether the historical data is waiting for the response
    const [isWaitingHistData, setIsWaitingHistData] = useState<boolean>(false);

    // handle click outside the container
    const handleClickOutside = useCallback(() => {
        setIsFocused(false);
    }, []);
    
    // use click outside hook to handle click outside the search board
    const clickOutsideRef = useClickOutside<HTMLDivElement>(handleClickOutside, isFocused);

    

    useEffect(() => {
        async function fetchYFinanceData() {
            if (symbol.length > 0) {
                const response = await axios.get(`/backend/api/v1/market/yfinance/exists?symbol=${symbol}`);

                if (response.data) {
                    // if exists, fetch public property info
                    const publicInfoResp = await axios.get(`/backend/api/v1/market/yfinance/get_public_prop_info?symbol=${symbol}`);
                    const publicInfo = publicInfoResp.data as PublicPropInfo;
                    setPublicPropInfo(publicInfo);
                } else {
                    setPublicPropInfo(null);
                }
            }
        }

        fetchYFinanceData();
    }, [symbol]);

    // search for historical data when user clicks the search board item
    useEffect(() => {
        if (selectedSymbol) {

            async function fetchHistData() {
                setIsWaitingHistData(true);
                const startDateStr = startDate.toISOString().split('T')[0];
                const endDateStr = endDate.toISOString().split('T')[0];
                const response = await axios.get(
                    `/backend/api/v1/market/yfinance/get_hist_data?symbol=${selectedSymbol}&start_date=${startDateStr}&end_date=${endDateStr}`
                );
                const histData = response.data as YFinancePricePoint[];
                
                // set the historical data to the state
                setHistData(histData);      
                setIsWaitingHistData(false);
            }
            
            fetchHistData();
        }

    }, [selectedSymbol, startDate, endDate]);

    return {
        symbol,
        setSymbol,
        isFocused,
        setIsFocused,
        publicPropInfo,
        setPublicPropInfo,
        selectedSymbol,
        setSelectedSymbol,
        histData,
        setHistData,
        isWaitingHistData,
        setIsWaitingHistData,
        clickOutsideRef,
    }
}