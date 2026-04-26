import { useState } from 'react';
import { Box, Card, Typography, CircularProgress, Select, MenuItem, FormControl } from '@mui/material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer
} from 'recharts';
import { PALETTE, C, chartProps } from '../theme';

export default function PriceTab({ data, loading }) {
  const [selectedTicker, setSelectedTicker] = useState(null);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, gap: 2 }}>
        <CircularProgress sx={{ color: C.accent }} size={20} />
        <Typography sx={{ color: C.muted, fontSize: '0.85rem' }}>Loading analytics…</Typography>
      </Box>
    );
  }
  if (!data) return null;

  const { tickers, ticker_names, monthly_dates, monthly_closes } = data;
  const activeTicker = selectedTicker || tickers[0];
  const activeIndex = tickers.indexOf(activeTicker);

  const normalizedData = monthly_dates.map((date, i) => {
    const point = { date };
    tickers.forEach(t => {
      const prices = monthly_closes[t];
      const base = prices.find(v => v !== null && v > 0);
      if (base !== undefined && prices[i] !== null) {
        point[t] = +((prices[i] / base) * 100).toFixed(2);
      }
    });
    return point;
  });

  const singleData = monthly_dates
    .map((date, i) => ({ date, price: monthly_closes[activeTicker]?.[i] ?? null }))
    .filter(d => d.price !== null);

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Price History
        </Typography>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <Select value={activeTicker} onChange={e => setSelectedTicker(e.target.value)}>
            {tickers.map(t => (
              <MenuItem key={t} value={t}>{ticker_names[t]}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Normalized multi-line */}
      <Card sx={{ p: 3, mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
          Indexed to 100 — All Stocks
        </Typography>
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={normalizedData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid {...chartProps.grid} />
            <XAxis dataKey="date" {...chartProps.axis} interval={Math.floor(monthly_dates.length / 8)} />
            <YAxis {...chartProps.axis} domain={['auto', 'auto']} />
            <Tooltip
              {...chartProps.tooltip}
              formatter={(val, name) => [val?.toFixed(1), ticker_names[name] || name]}
            />
            <Legend
              iconType="line"
              formatter={name => ticker_names[name] || name}
              {...chartProps.legend}
            />
            {tickers.map((t, i) => (
              <Line
                key={t}
                type="monotone"
                dataKey={t}
                stroke={PALETTE[i]}
                dot={false}
                strokeWidth={1.5}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Single stock raw close */}
      <Card sx={{ p: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
          {(ticker_names[activeTicker] || activeTicker).toUpperCase()} — Raw Close Price (MYR)
        </Typography>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={singleData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
            <CartesianGrid {...chartProps.grid} />
            <XAxis dataKey="date" {...chartProps.axis} interval={Math.floor(singleData.length / 8)} />
            <YAxis {...chartProps.axis} domain={['auto', 'auto']} tickFormatter={v => 'RM ' + v} />
            <Tooltip
              {...chartProps.tooltip}
              formatter={val => ['RM ' + val, ticker_names[activeTicker]]}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke={PALETTE[activeIndex]}
              dot={false}
              strokeWidth={2}
              connectNulls
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>
    </Box>
  );
}
