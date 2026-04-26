import {
  Box, Card, Typography, CircularProgress, Chip,
  Table, TableHead, TableBody, TableRow, TableCell
} from '@mui/material';
import { PALETTE, C } from '../theme';

const TH = {
  fontSize: '0.6rem', fontWeight: 700, color: C.muted,
  letterSpacing: 1, textTransform: 'uppercase', whiteSpace: 'nowrap',
  borderBottom: `1px solid ${C.border}`,
};

const TD = { fontSize: '0.8rem', color: C.text };

export default function StatsTab({ data, loading }) {
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

  return (
    <Box sx={{ p: 4 }}>
      <Typography sx={{ fontSize: '0.6rem', color: C.muted, letterSpacing: 1.5, textTransform: 'uppercase', mb: 3 }}>
        Descriptive Statistics — 3-Year Window
      </Typography>
      <Card sx={{ overflowX: 'auto' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={TH}>Company</TableCell>
              <TableCell sx={TH}>Ticker</TableCell>
              <TableCell sx={TH}>Current (MYR)</TableCell>
              <TableCell sx={TH}>Min</TableCell>
              <TableCell sx={TH}>Max</TableCell>
              <TableCell sx={TH}>Mean</TableCell>
              <TableCell sx={TH}>Std Dev (σ)</TableCell>
              <TableCell sx={TH}>3Y Return</TableCell>
              <TableCell sx={TH}>Avg Vol (M)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickers.map((ticker, i) => {
              const s = stats[ticker];
              const isPos = s.return_pct >= 0;
              return (
                <TableRow key={ticker}>
                  <TableCell sx={{ ...TD, fontWeight: 600, color: PALETTE[i], whiteSpace: 'nowrap' }}>
                    {ticker_names[ticker]}
                  </TableCell>
                  <TableCell sx={{ ...TD, color: C.muted }}>{ticker}</TableCell>
                  <TableCell sx={{ ...TD, fontWeight: 700, color: C.accent }}>MYR {s.current}</TableCell>
                  <TableCell sx={TD}>{s.min}</TableCell>
                  <TableCell sx={TD}>{s.max}</TableCell>
                  <TableCell sx={TD}>{s.mean}</TableCell>
                  <TableCell sx={TD}>{s.std}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${isPos ? '+' : ''}${s.return_pct}%`}
                      size="small"
                      sx={{
                        backgroundColor: isPos ? `${C.green}18` : `${C.red}18`,
                        color: isPos ? C.green : C.red,
                        border: `1px solid ${isPos ? C.green : C.red}40`,
                        fontWeight: 700,
                        fontSize: '0.68rem',
                      }}
                    />
                  </TableCell>
                  <TableCell sx={TD}>{s.mean_vol}M</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Card>
    </Box>
  );
}
