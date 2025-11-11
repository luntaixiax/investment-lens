import { AreaChart, Line, Area, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export type FxRate = {
    cur_dt: string; // Date in YYYY-MM-DD format
    rate: number;
}


export function CurrencyChart({ fxRates }: { fxRates: FxRate[] }) {
    return (
        <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={fxRates}>
                <XAxis 
                    dataKey="cur_dt" 
                    tick={{ fontSize: 12 }}
                    angle={-0}
                    textAnchor="end"
                    height={80}
                    interval={fxRates.length > 10 ? Math.floor(fxRates.length / 5) : 0}
                />
                <YAxis 
                    tick={{ fontSize: 12 }}
                    domain={fxRates.length > 0 ? (() => {
                        const rates = fxRates.map(r => r.rate);
                        const min = Math.min(...rates);
                        const max = Math.max(...rates);
                        const range = max - min;
                        return [min - range * 0.1, max + range * 0.1];
                    })() : [0, 'auto']}
                    tickFormatter={(value) => value.toFixed(4)}
                    width={60}
                />
                <Tooltip 
                    content={({ active, payload, label }) => {
                        if (active && payload && payload.length > 0) {
                            // Filter out Area entries - Line is typically the last entry since it's rendered after Area
                            // Or find entry that has a stroke color (Line has stroke, Area has stroke="none")
                            const linePayload = payload.find(p => {
                                // Check if this is the Line entry by looking for stroke property
                                return p.dataKey === 'rate' && p.value !== undefined && 
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
                                        <p style={{ margin: 0 }}>{Number(linePayload.value).toFixed(4)}</p>
                                    </div>
                                );
                            }
                        }
                        return null;
                    }}
                />
                <Legend 
                    content={({ payload }) => {
                        if (payload && payload.length > 0) {
                            // Filter to only show Line - find entry with stroke color
                            const linePayload = payload.find(p => {
                                return (p as any).stroke && (p as any).stroke !== 'none';
                            }) || payload[payload.length - 1]; // Fallback to last entry
                            
                            if (linePayload) {
                                return (
                                    <div style={{ textAlign: 'center', padding: '10px' }}>
                                        <span style={{ color: linePayload.color }}>Exchange Rate</span>
                                    </div>
                                );
                            }
                        }
                        return null;
                    }}
                />
                <defs>
                    <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#427a76" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#427a76" stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <Area 
                    type="monotone"
                    dataKey="rate"
                    fill="url(#colorRate)"
                    fillOpacity={0.4}
                    stroke="none"
                    connectNulls={false}
                    legendType="none"
                />
                <Line 
                    type="monotone"
                    dataKey="rate" 
                    name="Exchange Rate"
                    strokeWidth={3}
                    dot={false}
                    stroke="#427a76"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
}