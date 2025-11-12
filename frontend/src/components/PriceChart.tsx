import { AreaChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type PriceDataPoint = {
    [key: string]: string | number;
};

type PriceChartProps = {
    data: PriceDataPoint[];
    dateKey: string;
    priceKey: string;
    formatPrice?: (value: number) => string;
    formatYAxis?: (value: number) => string;
    gradientId?: string;
};

export function PriceChart({ 
    data, 
    dateKey, 
    priceKey,
    formatPrice = (value) => value.toFixed(2),
    formatYAxis = (value) => value.toFixed(2),
    gradientId = 'colorPrice'
}: PriceChartProps) {
    const domain = data.length > 0 ? (() => {
        const prices = data.map(d => Number(d[priceKey]));
        const min = Math.min(...prices);
        const max = Math.max(...prices);
        const range = max - min;
        return [min - range * 0.1, max + range * 0.1];
    })() : [0, 'auto'];

    return (
        <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data}>
                <XAxis 
                    dataKey={dateKey} 
                    tick={{ fontSize: 12 }}
                    angle={-0}
                    textAnchor="end"
                    height={80}
                    interval={data.length > 10 ? Math.floor(data.length / 5) : 0}
                />
                <YAxis 
                    tick={{ fontSize: 12 }}
                    domain={domain as [number, number]}
                    tickFormatter={formatYAxis}
                    width={60}
                />
                <Tooltip 
                    content={({ active, payload, label }) => {
                        if (active && payload && payload.length > 0) {
                            // Filter out Area entries - Line is typically the last entry since it's rendered after Area
                            // Or find entry that has a stroke color (Line has stroke, Area has stroke="none")
                            const linePayload = payload.find(p => {
                                // Check if this is the Line entry by looking for stroke property
                                return p.dataKey === priceKey && p.value !== undefined && 
                                       (p as any).stroke && (p as any).stroke !== 'none';
                            }) || payload[payload.length - 1]; // Fallback to last entry
                            
                            if (linePayload && linePayload.value !== undefined) {
                                return (
                                    <div className="custom-tooltip" style={{
                                        backgroundColor: '#fff',
                                        padding: '8px',
                                        border: '1px solid #ccc',
                                        borderRadius: '4px'
                                    }}>
                                        <p style={{ margin: 0, marginBottom: '4px', fontWeight: 'bold' }}>{label}</p>
                                        <p style={{ margin: 0 }}>{formatPrice(Number(linePayload.value))}</p>
                                    </div>
                                );
                            }
                        }
                        return null;
                    }}
                />
                <defs>
                    <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#427a76" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#427a76" stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <Area 
                    type="monotone"
                    dataKey={priceKey}
                    fill={`url(#${gradientId})`}
                    fillOpacity={0.4}
                    stroke="none"
                    connectNulls={false}
                    legendType="none"
                />
                <Line 
                    type="monotone"
                    dataKey={priceKey} 
                    name="Price"
                    strokeWidth={3}
                    dot={false}
                    stroke="#427a76"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}

