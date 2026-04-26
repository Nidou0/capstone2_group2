import { Box, Card, Typography, CircularProgress, Chip } from '@mui/material';
import { C } from '../theme';

function corrColor(v) {
  if (v >= 0.99) return '#c8f060';
  if (v > 0) return `rgba(200, 240, 96, ${(0.08 + v * 0.88).toFixed(2)})`;
  return `rgba(248, 113, 113, ${(0.08 + (-v) * 0.88).toFixed(2)})`;
}

export default function CorrelationTab({ data, loading, stocks }) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, gap: 2 }}>
        <CircularProgress sx={{ color: C.accent }} size={20} />
        <Typography sx={{ color: C.muted, fontSize: '0.85rem' }}>Loading analytics…</Typography>
      </Box>
    );
  }
  if (!data) return null;

  const { tickers, ticker_names, correlation } = data;
  const shortNames = tickers.map(t => t.replace('.KL', ''));
  const cellSize = 52;

  // Map ticker → signal for concordance analysis
  const signalMap = {};
  stocks.forEach(s => { signalMap[s.ticker] = s.direction; });

  // Find pairs that share the same non-HOLD signal and have correlation > 0.5
  const concordantPairs = [];
  for (let i = 0; i < tickers.length; i++) {
    for (let j = i + 1; j < tickers.length; j++) {
      const si = signalMap[shortNames[i]];
      const sj = signalMap[shortNames[j]];
      const corr = correlation[i][j];
      if (si && sj && si === sj && si !== 'HOLD' && si !== 'ERROR' && corr > 0.5) {
        concordantPairs.push({
          a: ticker_names[tickers[i]],
          b: ticker_names[tickers[j]],
          signal: si,
          corr,
        });
      }
    }
  }

  // Build flat cell list
  const cells = [];
  cells.push(<Box key="corner" sx={{ width: cellSize, height: cellSize }} />);
  shortNames.forEach((n, i) => cells.push(
    <Box key={`ch-${i}`} sx={{
      width: cellSize, height: cellSize,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: '9px', color: C.muted, fontWeight: 600, letterSpacing: 0.3,
    }}>
      {n}
    </Box>
  ));

  tickers.forEach((rowTicker, i) => {
    cells.push(
      <Box key={`rl-${i}`} sx={{
        width: cellSize, height: cellSize,
        display: 'flex', alignItems: 'center', justifyContent: 'flex-end',
        pr: 0.5, fontSize: '9px', color: C.muted, fontWeight: 600, letterSpacing: 0.3,
      }}>
        {shortNames[i]}
      </Box>
    );
    tickers.forEach((colTicker, j) => {
      const v = correlation[i][j];
      const si = signalMap[shortNames[i]];
      const sj = signalMap[shortNames[j]];
      const sameSignal = si && sj && si === sj && si !== 'HOLD' && si !== 'ERROR' && i !== j;
      cells.push(
        <Box
          key={`c-${i}-${j}`}
          title={`${ticker_names[rowTicker]} × ${ticker_names[colTicker]}: ${v.toFixed(2)}`}
          sx={{
            width: cellSize, height: cellSize,
            borderRadius: '4px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '9px',
            backgroundColor: corrColor(v),
            color: v > 0.5 ? '#0a0c0f' : C.text,
            cursor: 'default',
            outline: sameSignal ? `2px solid ${si === 'BUY' ? C.green : C.red}` : 'none',
            outlineOffset: '-2px',
            transition: 'transform 0.15s',
            '&:hover': { transform: 'scale(1.12)', zIndex: 2 },
          }}
        >
          {v.toFixed(2)}
        </Box>
      );
    });
  });

  return (
    <Box sx={{ p: 4 }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1.5, textTransform: 'uppercase', mb: 3 }}>
        Return Correlation Matrix
      </Typography>

      {/* Heatmap */}
      <Card sx={{ p: 3, mb: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 0.5 }}>
          Pairwise Correlation of Daily Returns
        </Typography>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, mb: 2 }}>
          Outlined cells = stocks sharing the same current signal
        </Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: `${cellSize}px `.repeat(tickers.length + 1).trim(),
            gap: '3px',
            width: 'fit-content',
          }}>
            {cells}
          </Box>
        </Box>
      </Card>

      {/* Signal concordance */}
      {concordantPairs.length > 0 && (
        <Card sx={{ p: 3, mb: 3 }}>
          <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 1.5 }}>
            Correlated Signal Pairs — Same Signal + Correlation &gt; 0.5
          </Typography>
          <Typography sx={{ fontSize: '0.68rem', color: C.muted, mb: 2, lineHeight: 1.6 }}>
            These pairs are likely driven by the same market move. Treat them as one position, not two independent signals.
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
            {concordantPairs.map((p, i) => (
              <Box key={i} sx={{
                display: 'flex', alignItems: 'center', gap: 1,
                backgroundColor: C.surface2,
                border: `1px solid ${p.signal === 'BUY' ? C.green : C.red}40`,
                borderRadius: '4px',
                px: 1.5, py: 0.8,
              }}>
                <Typography sx={{ fontSize: '0.7rem', color: C.text, fontWeight: 600 }}>
                  {p.a} × {p.b}
                </Typography>
                <Chip
                  label={p.signal}
                  size="small"
                  sx={{
                    height: 18,
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    backgroundColor: p.signal === 'BUY' ? `${C.green}20` : `${C.red}20`,
                    color: p.signal === 'BUY' ? C.green : C.red,
                  }}
                />
                <Typography sx={{ fontSize: '0.65rem', color: C.muted }}>
                  ρ = {p.corr.toFixed(2)}
                </Typography>
              </Box>
            ))}
          </Box>
        </Card>
      )}

      {/* Legend */}
      <Card sx={{ p: 3 }}>
        <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1, textTransform: 'uppercase', mb: 2 }}>
          Interpretation Guide
        </Typography>
        <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap', mb: 2 }}>
          {[
            { color: '#c8f060', label: 'Strong positive correlation' },
            { color: 'rgba(200,240,96,0.15)', label: 'Weak / no correlation' },
            { color: C.red, label: 'Negative correlation' },
          ].map(({ color, label }) => (
            <Box key={label} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box sx={{ width: 16, height: 16, borderRadius: '3px', backgroundColor: color, border: `1px solid ${C.border}` }} />
              <Typography sx={{ fontSize: '0.7rem', color: C.muted }}>{label}</Typography>
            </Box>
          ))}
        </Box>
        <Typography sx={{ fontSize: '0.7rem', color: C.muted, lineHeight: 1.8 }}>
          Banking stocks (Maybank, Public Bank, CIMB, Hong Leong) tend to correlate strongly.
          High correlation between stocks that both carry a BUY or SELL signal means less
          diversification — you are effectively taking one sector bet.
        </Typography>
      </Card>
    </Box>
  );
}
