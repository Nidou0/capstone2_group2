import { Box, Card, CardContent, Chip, Grid, Typography, CircularProgress } from '@mui/material';
import { PALETTE, C } from '../theme';

const ALL_TICKERS = ['1155', '1295', '1023', '5347', '5225', '8869', '5819', '5285', '6947', '5211'];

function RsiBlock({ rsi }) {
  const color = rsi < 30 ? C.green : rsi > 70 ? C.red : C.muted;
  const label = rsi < 30 ? 'Oversold' : rsi > 70 ? 'Overbought' : 'Neutral';
  return (
    <Box sx={{ flex: 1, textAlign: 'center' }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 0.8 }}>RSI</Typography>
      <Typography sx={{ fontSize: '0.9rem', fontWeight: 700, color, lineHeight: 1.2 }}>{rsi}</Typography>
      <Typography sx={{ fontSize: '0.58rem', color }}>{label}</Typography>
    </Box>
  );
}

function MacdBlock({ macd }) {
  const bullish = macd > 0;
  const color = bullish ? C.green : C.red;
  return (
    <Box sx={{ flex: 1, textAlign: 'center', borderLeft: `1px solid ${C.border}`, borderRight: `1px solid ${C.border}` }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 0.8 }}>MACD</Typography>
      <Typography sx={{ fontSize: '0.9rem', fontWeight: 700, color, lineHeight: 1.2 }}>{bullish ? '▲' : '▼'}</Typography>
      <Typography sx={{ fontSize: '0.58rem', color }}>{bullish ? 'Bullish' : 'Bearish'}</Typography>
    </Box>
  );
}

function BollingerBlock({ pos }) {
  const color = pos > 1.5 ? C.red : pos < -1.5 ? C.green : C.muted;
  const label = pos > 1.5 ? 'Above Band' : pos < -1.5 ? 'Below Band' : 'Mid-band';
  return (
    <Box sx={{ flex: 1, textAlign: 'center' }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 0.8 }}>BB POS</Typography>
      <Typography sx={{ fontSize: '0.9rem', fontWeight: 700, color, lineHeight: 1.2 }}>
        {pos > 0 ? '+' : ''}{pos}
      </Typography>
      <Typography sx={{ fontSize: '0.58rem', color }}>{label}</Typography>
    </Box>
  );
}

export default function PredictionsTab({ stocks, selectedTickers }) {
  if (stocks.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, gap: 2 }}>
        <CircularProgress sx={{ color: C.accent }} size={20} />
        <Typography sx={{ color: C.muted, fontSize: '0.85rem' }}>Loading predictions…</Typography>
      </Box>
    );
  }

  const filtered = stocks.filter(s => selectedTickers.includes(s.ticker));

  return (
    <Box sx={{ p: 4 }}>
      <Grid container spacing={3}>
        {filtered.map(stock => {
          const idx = ALL_TICKERS.indexOf(stock.ticker);
          const accentColor = PALETTE[idx >= 0 ? idx : 0];
          const isPos = stock.pct_change >= 0;
          const dirColor = stock.direction === 'BUY' ? C.green : stock.direction === 'SELL' ? C.red : C.muted;

          return (
            <Grid item xs={12} md={6} xl={4} key={stock.ticker}>
              <Card sx={{
                borderLeft: `3px solid ${accentColor}`,
                transition: 'border-color 0.2s, background 0.2s',
                '&:hover': { backgroundColor: C.surface2 },
              }}>
                <CardContent sx={{ p: 2.5 }}>

                  {/* Header */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: accentColor, letterSpacing: -0.2 }}>
                        {stock.ticker}
                      </Typography>
                      <Typography sx={{ fontSize: '0.8rem', color: C.text, fontWeight: 500 }}>
                        {stock.name}
                      </Typography>
                      <Typography sx={{ fontSize: '0.65rem', color: C.muted }}>Bursa Malaysia</Typography>
                    </Box>
                    <Chip
                      label={stock.direction || 'HOLD'}
                      size="small"
                      sx={{
                        fontWeight: 700,
                        backgroundColor: `${dirColor}18`,
                        color: dirColor,
                        border: `1px solid ${dirColor}40`,
                      }}
                    />
                  </Box>

                  {/* Prices */}
                  <Box sx={{ display: 'flex', gap: 4, mb: 2.5 }}>
                    <Box>
                      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 0.8 }}>CURRENT CLOSE</Typography>
                      <Typography sx={{ fontSize: '1.1rem', fontWeight: 700, color: C.text, mt: 0.3 }}>
                        RM {stock.current_price}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 0.8 }}>PREDICTED CLOSE</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mt: 0.3 }}>
                        <Typography sx={{ fontSize: '1.1rem', fontWeight: 700, color: accentColor }}>
                          RM {stock.end_close_price}
                        </Typography>
                        <Typography sx={{ fontSize: '0.75rem', fontWeight: 700, color: isPos ? C.green : C.red }}>
                          {isPos ? '+' : ''}{stock.pct_change}%
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  {/* Indicator row */}
                  <Box sx={{
                    display: 'flex',
                    pt: 2,
                    borderTop: `1px solid ${C.border}`,
                  }}>
                    <RsiBlock rsi={stock.rsi} />
                    <MacdBlock macd={stock.macd_hist} />
                    <BollingerBlock pos={stock.bollinger_pos} />
                  </Box>

                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
}
