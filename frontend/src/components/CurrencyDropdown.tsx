import './CurrencyDropdown.css';
import { useState, useCallback } from 'react';
import { useClickOutside } from '../hooks/ClickOutSide';
import { CURRENCIES } from '../utils/enums';
import type { Currency } from '../utils/models';



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