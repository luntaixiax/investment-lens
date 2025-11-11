import './CurrencyDropdown.css';
import { useState, useCallback } from 'react';
import { useClickOutside } from '../hooks/ClickOutSide';

export type Currency = {
    symbol: string;
    id: number;
    flagClass: string;
}

export const CURRENCIES: Currency[] = [
    { symbol: 'USD', id: 1, flagClass: 'fi-us' },
    { symbol: 'CAD', id: 2, flagClass: 'fi-ca' },
    { symbol: 'CNY', id: 3, flagClass: 'fi-cn' },
    { symbol: 'GBP', id: 4, flagClass: 'fi-gb' },
    { symbol: 'AUD', id: 5, flagClass: 'fi-au' },
    { symbol: 'JPY', id: 6, flagClass: 'fi-jp' },
    { symbol: 'EUR', id: 7, flagClass: 'fi-eu' },
    { symbol: 'MOP', id: 8, flagClass: 'fi-mo' },
    { symbol: 'HKD', id: 9, flagClass: 'fi-hk' },
    { symbol: 'CHF', id: 10, flagClass: 'fi-ch' },
    { symbol: 'TWD', id: 11, flagClass: 'fi-tw' },
    { symbol: 'THB', id: 12, flagClass: 'fi-th' },
    { symbol: 'MXN', id: 13, flagClass: 'fi-mx' },
    { symbol: 'CUP', id: 14, flagClass: 'fi-cu' },
    { symbol: 'RUB', id: 15, flagClass: 'fi-ru' },
]



type props = {
    label: string;
    selected: Currency;
    onSelect: (currency: Currency) => void;
}

export default function CurrencyDropdown({ label, selected, onSelect }: props) {
    const [isOpen, setIsOpen] = useState(false);
    const closeDropdown = useCallback(() => setIsOpen(false), []);
    const dropdownRef = useClickOutside<HTMLDivElement>(closeDropdown);

    const handleSelect = (currency: Currency) => {
        onSelect(currency);
        setIsOpen(false);
    };

    return (
        <div className="currency-dropdown-container">
            <label className="currency-dropdown-label">{label}</label>
            <div className="currency-dropdown-wrapper" ref={dropdownRef}>
                <button
                    type="button"
                    className="currency-dropdown-button"
                    onClick={() => setIsOpen(!isOpen)}
                    aria-haspopup="listbox"
                    aria-expanded={isOpen}
                >
                    <span className={`fi ${selected.flagClass}`}></span>
                    <span>{selected.symbol}</span>
                    <span className="currency-dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
                </button>
                {isOpen && (
                    <ul className="currency-dropdown-list" role="listbox">
                        {CURRENCIES.map(currency => (
                            <li
                                key={currency.id}
                                className={`currency-dropdown-item ${selected.id === currency.id ? 'selected' : ''}`}
                                onClick={() => handleSelect(currency)}
                                role="option"
                                aria-selected={selected.id === currency.id}
                            >
                                <span className={`fi ${currency.flagClass}`}></span>
                                <span>{currency.symbol}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    )
}