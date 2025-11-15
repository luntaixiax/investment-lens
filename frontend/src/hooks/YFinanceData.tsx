import { useState, useEffect } from 'react';
import axios from 'axios';
import type { PublicPropInfo } from '../utils/models';
import type { YFinancePricePoint } from '../utils/models';

export function useYFinanceSearch(searchSymbol: string) {

    // public property information
    const [publicPropInfos, setPublicPropInfos] = useState<PublicPropInfo[]>([]);

    useEffect(() => {
        async function fetchYFinanceData() {
            if (searchSymbol.length > 0) {
                const response = await axios.get(`/backend/api/v1/registry/blurry_search_yfinance?keyword=${searchSymbol}`);
                const publicInfos = response.data as PublicPropInfo[];
                setPublicPropInfos(publicInfos);
            }
        }

        fetchYFinanceData();
    }, [searchSymbol]);

    return {
        publicPropInfos,
    }
}

export function useYFinanceData(selectedSymbol: string | null, startDate: Date, endDate: Date) {


    // public property information
    const [publicPropInfo, setPublicPropInfo] = useState<PublicPropInfo | null>(null);
    // historical data for the selected symbol
    const [histData, setHistData] = useState<YFinancePricePoint[]>([]);
    // whether the historical data is waiting for the response
    const [isWaitingHistData, setIsWaitingHistData] = useState<boolean>(false);

    

    useEffect(() => {
        async function fetchYFinanceData() {
            if (selectedSymbol) {
                const response = await axios.get(`/backend/api/v1/market/yfinance/exists?symbol=${selectedSymbol}`);

                if (response.data) {
                    // if exists, fetch public property info
                    const publicInfoResp = await axios.get(`/backend/api/v1/market/yfinance/get_public_prop_info?symbol=${selectedSymbol}`);
                    const publicInfo = publicInfoResp.data as PublicPropInfo;
                    setPublicPropInfo(publicInfo);
                } else {
                    setPublicPropInfo(null);
                }
            }
        }

        fetchYFinanceData();
    }, [selectedSymbol]);

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
        selectedPublicPropInfo: publicPropInfo,
        histData,
        isWaitingHistData,
    }
}