import './CurrencySection.css';
import CurrencyDropdown from './CurrencyDropdown';
import { CurrencyChart } from './CurrencyChart';
import { useCurrencyData } from '../hooks/CurrencyData';

export const CurrencySection = () => {
    const { fromCurrency, toCurrency, setFromCurrency, setToCurrency, 
        fxRates, currentFxRate, selectedPeriod, setSelectedPeriod, periods 
    } = useCurrencyData();

    return (
        <section className="market-page-container">
            <h1>Currency Rates</h1>
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
                <div className="period-toolbar">
                    {periods.map((period) => (
                        <button
                            key={period}
                            className={`period-button ${selectedPeriod === period ? 'active' : ''}`}
                            onClick={() => setSelectedPeriod(period)}
                        >
                            {period}
                        </button>
                    ))}
                </div>
                <CurrencyChart fxRates={fxRates} />
            </div>
        </section>
    )
}