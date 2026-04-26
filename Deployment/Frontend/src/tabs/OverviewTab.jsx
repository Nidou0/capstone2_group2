import { Box, Card, CardContent, Grid, Typography, CircularProgress } from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine
} from 'recharts';
import { PALETTE, C, chartProps } from '../theme';

export default function OverviewTab({ data, loading, stocks }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, gap: 2 }}>
        <CircularProgress sx={{ color: C.accent }} size={20} />
        <Typography sx={{ color: C.muted, fontSize: '0.85rem' }}>Loading analytics…</Typography>
      </Box>
    );
  }
  if (!data) return null;

  const { tickers, ticker_names, stats } = data;

  const returnsData = tickers.map(t => ({ name: t.replace('.KL', ''), value: stats[t].return_pct }));

  // RSI chart — replaces avg volume: directly tied to model features
  const rsiData = tickers.map((t, i) => {
    const shortTicker = t.replace('.KL', '');
    const stockRsi = stocks.find(s => s.ticker === shortTicker)?.rsi ?? null;
    return { name: shortTicker, rsi: stockRsi };
  }).filter(d => d.rsi !== null);

  const maxStd = Math.max(...tickers.map(t => stats[t].std));
  const globalMax = Math.max(...tickers.map(t => stats[t].max));

  return (
    <Box sx={{ p: 4 }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1.5, textTransform: 'uppercase', mb: 3 }}>
        Portfolio Snapshot
      </Typography>

      {/* Stock summary cards */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {tickers.map((ticker, i) => {
          const s = stats[ticker];
          const isPos = s.return_pct >= 0;
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={ticker}>
              <Card sx={{
                borderLeft: `3px solid ${PALETTE[i]}`,
                '&:hover': { backgroundColor: C.surface2 },
                transition: 'background 0.2s',
              }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                    <Box>
                      <Typography sx={{ fontWeight: 700, fontSize: '0.95rem', color: PALETTE[i] }}>
                        {ticker.replace('.KL', '')}
                      </Typography>
                      <Typography sx={{ fontSize: '0.68rem', color: C.muted }}>
                        {ticker_names[ticker]}
                      </Typography>
                    </Box>
                    <Typography sx={{ fontWeight: 700, fontSize: '0.95rem', color: isPos ? C.green : C.red }}>
                      {isPos ? '+' : ''}{s.return_pct}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography sx={{ fontSize: '0.65rem', color: C.muted }}>Current</Typography>
                    <Typography sx={{ fontSize: '0.65rem', color: C.text }}>MYR {s.current}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography sx={{ fontSize: '0.65rem', color: C.muted }}>Range</Typography>
                    <Typography sx={{ fontSize: '0.65rem', color: C.text }}>{s.min} – {s.max}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                    <Typography sx={{ fontSize: '0.65rem', color: C.muted }}>Avg Vol</Typography>
                    <Typography sx={{ fontSize: '0.65rem', color: C.text }}>{s.mean_vol}M</Typography>
                  </Box>
                  <Box sx={{ height: 2, backgroundColor: C.border, borderRadius: 1 }}>
                    <Box sx={{
                      height: '100%',
                      width: `${(s.std / maxStd * 100).toFixed(1)}%`,
                      backgroundColor: PALETTE[i],
                      borderRadius: 1,
                    }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Charts: Returns + RSI */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3 }}>
            <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
              3-Year Returns (%)
            </Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={returnsData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid {...chartProps.grid} />
                <XAxis dataKey="name" {...chartProps.axis} />
                <YAxis {...chartProps.axis} tickFormatter={v => v + '%'} />
                <ReferenceLine y={0} stroke={C.border} />
                <Tooltip {...chartProps.tooltip} formatter={v => [v + '%', 'Return']} />
                <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                  {returnsData.map((e, idx) => (
                    <Cell key={`r-${idx}`} fill={e.value >= 0 ? C.green : C.red} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3 }}>
            <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 0.5 }}>
              RSI — Current Readings (Model Feature)
            </Typography>
            <Typography sx={{ fontSize: '0.6rem', color: C.muted, mb: 2 }}>
              &lt;30 oversold · &gt;70 overbought
            </Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={rsiData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid {...chartProps.grid} />
                <XAxis dataKey="name" {...chartProps.axis} />
                <YAxis {...chartProps.axis} domain={[0, 100]} />
                <ReferenceLine y={30} stroke={C.green} strokeDasharray="4 2" strokeOpacity={0.5} />
                <ReferenceLine y={70} stroke={C.red} strokeDasharray="4 2" strokeOpacity={0.5} />
                <Tooltip {...chartProps.tooltip} formatter={v => [v, 'RSI']} />
                <Bar dataKey="rsi" radius={[3, 3, 0, 0]}>
                  {rsiData.map((e, idx) => (
                    <Cell key={`rsi-${idx}`} fill={e.rsi < 30 ? C.green : e.rsi > 70 ? C.red : PALETTE[idx]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>

      {/* Distribution bars */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3 }}>
            <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
              Volatility — Std Dev of Close (Rolling CV Feature)
            </Typography>
            {tickers.map((ticker, i) => (
              <Box key={ticker} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                <Typography sx={{ width: 88, fontSize: '0.65rem', color: C.muted, textAlign: 'right', flexShrink: 0 }}>
                  {ticker_names[ticker].split(' ')[0]}
                </Typography>
                <Box sx={{ flex: 1, height: 10, backgroundColor: C.border, borderRadius: 1, overflow: 'hidden' }}>
                  <Box sx={{
                    height: '100%',
                    width: `${(stats[ticker].std / maxStd * 100).toFixed(1)}%`,
                    backgroundColor: PALETTE[i],
                    borderRadius: 1,
                  }} />
                </Box>
                <Typography sx={{ width: 58, fontSize: '0.65rem', color: C.text, flexShrink: 0 }}>
                  σ = {stats[ticker].std}
                </Typography>
              </Box>
            ))}
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ p: 3 }}>
            <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
              Price Range (Min → Max, MYR)
            </Typography>
            {tickers.map((ticker, i) => {
              const minPct = (stats[ticker].min / globalMax * 100).toFixed(1);
              const widthPct = ((stats[ticker].max - stats[ticker].min) / globalMax * 100).toFixed(1);
              return (
                <Box key={ticker} sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                  <Typography sx={{ width: 88, fontSize: '0.65rem', color: C.muted, textAlign: 'right', flexShrink: 0 }}>
                    {ticker_names[ticker].split(' ')[0]}
                  </Typography>
                  <Box sx={{ flex: 1, height: 10, backgroundColor: C.border, borderRadius: 1, position: 'relative' }}>
                    <Box sx={{
                      position: 'absolute',
                      left: `${minPct}%`,
                      width: `${widthPct}%`,
                      height: '100%',
                      backgroundColor: PALETTE[i],
                      borderRadius: 1,
                    }} />
                  </Box>
                  <Typography sx={{ width: 78, fontSize: '0.65rem', color: C.text, flexShrink: 0 }}>
                    {stats[ticker].min}–{stats[ticker].max}
                  </Typography>
                </Box>
              );
            })}
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
