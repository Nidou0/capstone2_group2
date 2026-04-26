import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import './index.css';
import App from './App.jsx';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#0a0c0f', paper: '#111318' },
    primary:    { main: '#c8f060', contrastText: '#0a0c0f' },
    secondary:  { main: '#60c8f0' },
    success:    { main: '#4ade80' },
    error:      { main: '#f87171' },
    text:       { primary: '#e8eaf0', secondary: '#6b7280' },
    divider:    '#1f2530',
  },
  typography: {
    fontFamily: "'DM Mono', monospace",
  },
  shape: { borderRadius: 6 },
  components: {
    MuiCssBaseline: {
      styleOverrides: { body: { backgroundColor: '#0a0c0f' } },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#111318',
          border: '1px solid #1f2530',
          boxShadow: 'none',
          '&:hover': { borderColor: '#2f3540' },
        },
      },
    },
    MuiCheckbox: {
      styleOverrides: {
        root: {
          color: '#2f3540',
          '&.Mui-checked': { color: '#c8f060' },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: { backgroundColor: '#c8f060' },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          color: '#6b7280',
          textTransform: 'none',
          fontSize: '0.78rem',
          fontWeight: 500,
          letterSpacing: 0.3,
          minWidth: 100,
          '&.Mui-selected': { color: '#c8f060' },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: { borderBottomColor: '#1a1f28' },
        head: { backgroundColor: '#0a0c0f', color: '#6b7280' },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: { '&:hover': { backgroundColor: '#181c24' } },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          fontSize: '0.82rem',
          '& .MuiOutlinedInput-notchedOutline': { borderColor: '#1f2530' },
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#2f3540' },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#c8f060' },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: { fontSize: '0.82rem', '&:hover': { backgroundColor: '#181c24' } },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontFamily: "'DM Mono', monospace", fontSize: '0.72rem' },
      },
    },
  },
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
);
