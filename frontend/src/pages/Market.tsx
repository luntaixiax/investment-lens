import './Market.css';
import { useState } from 'react';
import NavBarLogin from "../components/NavBarLogin";
import { CurrencySection } from "../components/CurrencySection";
import { YFinanceSection } from "../components/YFinanceSection";

type Tab = 'currency' | 'yfinance';

export default function Market() {
    const [activeTab, setActiveTab] = useState<Tab>('currency');

    return (
        <>
            <NavBarLogin />
            <section className="market-page-container">
                <div className="market-tabs">
                    <button
                        className={`market-tab ${activeTab === 'currency' ? 'active' : ''}`}
                        onClick={() => setActiveTab('currency')}
                    >
                        Exchange Rates
                    </button>
                    <button
                        className={`market-tab ${activeTab === 'yfinance' ? 'active' : ''}`}
                        onClick={() => setActiveTab('yfinance')}
                    >
                        Financial Markets
                    </button>
                </div>
                <div className="market-tab-content">
                    {activeTab === 'currency' && <CurrencySection />}
                    {activeTab === 'yfinance' && <YFinanceSection />}
                </div>
            </section>
        </>
    )
}