import './YFinanceSection.css';
import { useState } from 'react';
import { PeriodToolbar } from './PeriodToolbar';
import { PriceChart } from './PriceChart';
import { useYFinanceData } from '../hooks/YFinanceData';
import { CURRENCIES, getPropTypeByValue } from '../utils/enums';
import { usePeriodSelection } from '../hooks/PeriodSelection';

export function YFinanceSection() {
    const [isDescriptionExpanded, setIsDescriptionExpanded] = useState<boolean>(false);

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
                selectedSymbol === symbol && publicPropInfo && (
                    <section className="yfinance-details-section">

                        <div className="yfinance-info-container">
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Name</span>
                                <span className="yfinance-info-item-value">{publicPropInfo?.name ? publicPropInfo.name : '-'}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Exchange</span>
                                <span className="yfinance-info-item-value">{publicPropInfo?.exchange ? publicPropInfo.exchange : '-'}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Currency</span>
                                <span className="yfinance-info-item-value">{CURRENCIES.find(c => c.id === publicPropInfo.currency)?.symbol}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Prop Type</span>
                                <span className="yfinance-info-item-value">{getPropTypeByValue(publicPropInfo?.prop_type)}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Industry</span>
                                <span className="yfinance-info-item-value">{publicPropInfo?.industry ? publicPropInfo.industry : '-'}</span>    
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Sector</span>
                                <span className="yfinance-info-item-value">{publicPropInfo?.sector ? publicPropInfo.sector : '-'}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Country</span>
                                <span className="yfinance-info-item-value">{publicPropInfo?.country ? publicPropInfo.country : '-'}</span>
                            </div>
                            <div className="yfinance-info-item">
                                <span className="yfinance-info-item-label">Website</span>
                                {publicPropInfo?.website? (
                                    <a className="yfinance-info-item-value" href={publicPropInfo?.website} target="_blank" rel="noopener noreferrer">
                                        Click to visit
                                    </a>
                                ) : (
                                    <span className="yfinance-info-item-value">-</span>
                                )}
                            </div>
                        </div>

                        {publicPropInfo?.description && (
                            <div className="yfinance-info-item yfinance-description-item">
                                <div 
                                    className="yfinance-description-header"
                                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                                >
                                    <span className="yfinance-info-item-label">Description</span>
                                    <button className="yfinance-expand-button">
                                        <i className={`fa-solid fa-chevron-${isDescriptionExpanded ? 'up' : 'down'}`}></i>
                                    </button>
                                </div>
                                <div className={`yfinance-description-content ${isDescriptionExpanded ? 'expanded' : 'collapsed'}`}>
                                    <span className="yfinance-info-item-value">{publicPropInfo.description}</span>
                                </div>
                            </div>
                        )}

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
                                    tooltipFields={[
                                        { key: 'raw_close', label: 'Raw Close', formatter: (v) => `$${v.toFixed(2)}` },
                                        { key: 'adj_close', label: 'Adj Close', formatter: (v) => `$${v.toFixed(2)}` },
                                        { key: 'volume', label: 'Volume', formatter: (v) => v.toLocaleString() },
                                        { key: 'dividends', label: 'Dividends', formatter: (v) => v > 0 ? `$${v.toFixed(2)}` : '-' },
                                        { key: 'stock_splits', label: 'Stock Splits', formatter: (v) => v > 0 ? v.toFixed(2) : '-' },
                                        { key: 'split_factor', label: 'Split Factor', formatter: (v) => v.toFixed(4) }
                                    ]}
                                />
                            ) : (
                                <p>No historical data found</p>
                            )}
                        </div>
                    </section>
                )
            }


        </section>
    )
}