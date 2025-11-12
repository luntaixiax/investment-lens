import './CurrencySection.css';
import CurrencyDropdown from './CurrencyDropdown';
import { PriceChart } from './PriceChart';
import { PeriodToolbar } from './PeriodToolbar';
import { useCurrencyData } from '../hooks/CurrencyData';
import { usePeriodSelection } from '../hooks/PeriodSelection';

export const CurrencySection = () => {

    // get period selection
    const { 
        selectedPeriod,
        setSelectedPeriod,
        periods,
        startDate, 
        endDate 
    } = usePeriodSelection('3M');

    const { fromCurrency, toCurrency, setFromCurrency, setToCurrency, 
        fxRates, currentFxRate 
    } = useCurrencyData(startDate, endDate);

    return (
        <section className="currency-container">
            <div className="currencies-dropdown-container">
                <CurrencyDropdown 
                    label="From Currency" 
                    selected={fromCurrency} 
                    onSelect={setFromCurrency} 
                />
                <CurrencyDropdown 
                    label="To Currency" 
                    selected={toCurrency} 
                    onSelect={setToCurrency} 
                />
                <div className="current-fx-rate-container">
                    <p>As of { } 
                        {fxRates.length > 0 && (
                            <span className="current-fx-rate-date">{fxRates[fxRates.length - 1].cur_dt}</span>
                        )}
                    </p>
                    <p>
                        1 {fromCurrency.symbol} = &nbsp;
                        <span className="current-fx-rate-value">{currentFxRate.toFixed(4)}</span> 
                        &nbsp;{toCurrency.symbol}
                    </p>
                </div>
            </div>

            <div className="chart-container">

                <div className="chart-toolbar">
                    <div className="chart-header-title">
                        <h3>{fromCurrency.symbol} / {toCurrency.symbol}</h3>
                        <p>{startDate.toISOString().split('T')[0]} - {endDate.toISOString().split('T')[0]}</p>
                    </div>
                    <PeriodToolbar 
                        periods={periods}
                        selectedPeriod={selectedPeriod}
                        onPeriodChange={setSelectedPeriod}
                    />
                </div>

                <PriceChart
                    data={fxRates}
                    dateKey="cur_dt"
                    priceKey="rate"
                    formatPrice={(value) => value.toFixed(4)}
                    formatYAxis={(value) => value.toFixed(4)}
                    gradientId="colorRate"
                />
            </div>
        </section>
    )
}