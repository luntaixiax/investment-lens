import './PeriodToolBar.css';
import { type TimePeriod } from '../hooks/PeriodSelection';

type PeriodToolbarProps = {
    periods: TimePeriod[];
    selectedPeriod: TimePeriod;
    onPeriodChange: (period: TimePeriod) => void;
};

export function PeriodToolbar({ periods, selectedPeriod, onPeriodChange }: PeriodToolbarProps) {
    return (
        <div className="period-toolbar">
            {periods.map((period) => (
                <button
                    key={period}
                    className={`period-button ${selectedPeriod === period ? 'active' : ''}`}
                    onClick={() => onPeriodChange(period)}
                >
                    {period}
                </button>
            ))}
        </div>
    );
}

