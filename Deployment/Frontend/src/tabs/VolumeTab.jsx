import { useState } from 'react';
import { Box, Card, Typography, CircularProgress, Select, MenuItem, FormControl } from '@mui/material';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { PALETTE, C, chartProps } from '../theme';

export default function VolumeTab({ data, loading }) {
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

  const { tickers, ticker_names, recent_dates, recent_volumes, stats } = data;
  const activeTicker = selectedTicker || tickers[0];
  const activeIndex = tickers.indexOf(activeTicker);
  const maxVol = Math.max(...tickers.map(t => stats[t].mean_vol));

  const volSeriesData = recent_dates.map((date, i) => ({
    date,
    volume: recent_volumes[activeTicker]?.[i] ?? 0,
  }));

  // Volume momentum: day-over-day % change in volume
  const momentumData = volSeriesData.map((d, i) => {
    const prev = i > 0 ? volSeriesData[i - 1].volume : null;
    const mom = prev && prev > 0 ? +((( d.volume - prev) / prev) * 100).toFixed(1) : 0;
    return { date: d.date, momentum: mom };
  }).slice(1);

  return (
    <Box sx={{ p: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Volume Analysis
        </Typography>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <Select value={activeTicker} onChange={e => setSelectedTicker(e.target.value)}>
            {tickers.map(t => <MenuItem key={t} value={t}>{ticker_names[t]}</MenuItem>)}
          </Select>
        </FormControl>
      </Box>

      {/* 60-day volume bar chart */}
      <Card sx={{ p: 3, mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
          Daily Volume — Last 60 Trading Days (M Shares)
        </Typography>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={volSeriesData} margin={{ top: 4, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid {...chartProps.grid} />
            <XAxis dataKey="date" {...chartProps.axis} interval={Math.floor(recent_dates.length / 10)} />
            <YAxis {...chartProps.axis} tickFormatter={v => v + 'M'} />
            <Tooltip {...chartProps.tooltip} formatter={v => [v + 'M', 'Volume']} />
            <Bar dataKey="volume" fill={PALETTE[activeIndex]} radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Volume momentum chart — day-over-day % change (model uses Volume_log_returns) */}
      <Card sx={{ p: 3, mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 0.5 }}>
          Volume Momentum — Day-over-Day Change % (Volume Log Returns Feature)
        </Typography>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, mb: 2 }}>
          Positive = volume accelerating · Negative = volume declining
        </Typography>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={momentumData} margin={{ top: 4, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid {...chartProps.grid} />
            <XAxis dataKey="date" {...chartProps.axis} interval={Math.floor(momentumData.length / 10)} />
            <YAxis {...chartProps.axis} tickFormatter={v => v + '%'} />
            <ReferenceLine y={0} stroke={C.border} strokeWidth={1.5} />
            <Tooltip {...chartProps.tooltip} formatter={v => [v + '%', 'Vol Δ']} />
            <Line
              type="monotone"
              dataKey="momentum"
              stroke={PALETTE[activeIndex]}
              dot={false}
              strokeWidth={1.5}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Volume distribution */}
      <Card sx={{ p: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
          Volume Distribution — 3Y Daily Avg (M Shares)
        </Typography>
        {tickers.map((ticker, i) => (
          <Box key={ticker} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
            <Typography sx={{ width: 100, fontSize: '0.65rem', color: C.muted, textAlign: 'right', flexShrink: 0 }}>
              {ticker_names[ticker].split(' ')[0]}
            </Typography>
            <Box sx={{ flex: 1, height: 12, backgroundColor: C.border, borderRadius: 1, overflow: 'hidden' }}>
              <Box sx={{
                height: '100%',
                width: `${(stats[ticker].mean_vol / maxVol * 100).toFixed(1)}%`,
                backgroundColor: PALETTE[i],
                borderRadius: 1,
              }} />
            </Box>
            <Typography sx={{ width: 55, fontSize: '0.65rem', color: C.text, flexShrink: 0 }}>
              {stats[ticker].mean_vol}M
            </Typography>
          </Box>
        ))}
      </Card>
    </Box>
  );
}
