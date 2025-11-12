import './YFinanceSection.css';
import { PeriodToolbar } from './PeriodToolbar';
import { PriceChart } from './PriceChart';
import { useYFinanceData } from '../hooks/YFinanceData';
import { CURRENCIES, getPropTypeByValue } from '../utils/enums';
import { usePeriodSelection } from '../hooks/PeriodSelection';

export function YFinanceSection() {

    // get period selection
    const { 
        selectedPeriod,
        setSelectedPeriod,
        periods,
        startDate, 
        endDate 
    } = usePeriodSelection('3M');
   
    // get yfinance data hook
    const { 
        symbol,
        setSymbol,
        isFocused,
        setIsFocused,
        publicPropInfo,
        selectedSymbol,
        setSelectedSymbol,
        histData,
        isWaitingHistData,
        clickOutsideRef,
    } = useYFinanceData(startDate, endDate);

    
    return (
        <section className="yfinance-section">
            <div className="yfinance-search-bar-container" ref={clickOutsideRef}>
                <div className="yfinance-search-bar">
                    <input 
                        type="text" 
                        placeholder="Enter a symbol to search" 
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                    />
                    <button className="search-button">
                        <i className="fa-solid fa-magnifying-glass"></i>
                    </button>
                </div>

                {isFocused && (
                    publicPropInfo ? (
                        <div 
                            className="yfinance-search-board"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => setSelectedSymbol(publicPropInfo.symbol)}
                        >
                            <div className="yfinance-search-board-item">
                                <div className="yfinance-search-board-item-header">
                                    <span className="yfinance-search-board-item-symbol">{publicPropInfo.symbol}</span>
                                    <div className="yfinance-search-board-item-tags">
                                        <span className={`fi ${CURRENCIES.find(c => c.id === publicPropInfo.currency)?.flagClass}`}></span>
                                        <span className="yfinance-search-board-item-prop-type">{getPropTypeByValue(publicPropInfo.prop_type)}</span>
                                        <span className="yfinance-search-board-item-exchange">{publicPropInfo.exchange}</span>
                                    </div>
                                </div>
                                <span className="yfinance-search-board-item-name">{publicPropInfo.name}</span>
                            </div>
                        </div>
                    ) : (
                        <div 
                            className="yfinance-search-board"
                            onMouseDown={(e) => e.preventDefault()}
                        >
                            <div className="yfinance-search-board-item">
                                <span className="yfinance-search-board-item-symbol">No results found</span>
                            </div>
                        </div>
                    )
                )}
            </div>


            {
                selectedSymbol && (
                    <div className="chart-container">
                        <div className="chart-toolbar">
                            <div className="chart-header-title">
                                <h3>{selectedSymbol}</h3>
                                <p>{startDate.toISOString().split('T')[0]} - {endDate.toISOString().split('T')[0]}</p>
                            </div>
                            <PeriodToolbar 
                                periods={periods}
                                selectedPeriod={selectedPeriod}
                                onPeriodChange={setSelectedPeriod}
                            />
                        </div>

                        {isWaitingHistData ? (
                            <i className="fa-solid fa-spinner fa-spin"></i>
                        ) : histData.length > 0 ? (
                            <PriceChart
                                data={histData}
                                dateKey="dt"
                                priceKey="close"
                                formatPrice={(value) => `$${value.toFixed(2)}`}
                                formatYAxis={(value) => value.toFixed(2)}
                                gradientId="colorPrice"
                            />
                        ) : (
                            <p>No historical data found</p>
                        )}
                    </div>
                )
            }


        </section>
    )
}