import './Market.css';
import NavBarLogin from "../components/NavBarLogin";
import CurrencyDropdown from "../components/CurrencyDropdown";
import { CurrencyChart } from "../components/CurrencyChart";
import { useCurrencyData } from "../hooks/CurrencyData";

export default function Market() {
    const {
        fromCurrency,
        setFromCurrency,
        toCurrency,
        setToCurrency,
        selectedPeriod,
        setSelectedPeriod,
        fxRates,
        currentFxRate,
        periods,
    } = useCurrencyData();

    return (
        <>
            <NavBarLogin />
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
        </>
    )
}