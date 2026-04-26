import { useState, useEffect } from 'react';
import { Typography, Box, Checkbox, FormGroup, FormControlLabel, Tabs, Tab } from '@mui/material';
import PredictionsTab from './tabs/PredictionsTab';
import OverviewTab from './tabs/OverviewTab';
import PriceTab from './tabs/PriceTab';
import VolumeTab from './tabs/VolumeTab';
import StatsTab from './tabs/StatsTab';
import CorrelationTab from './tabs/CorrelationTab';

const TABS = ['Predictions', 'Overview', 'Price History', 'Volume', 'Stats', 'Correlation'];

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [stocks, setStocks] = useState([]);
  const [selectedTickers, setSelectedTickers] = useState([]);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await fetch('/api/stocks');
        const data = await res.json();
        setStocks(data);
        setSelectedTickers(data.map(s => s.ticker));
      } catch (e) {
        console.error('Error fetching stocks:', e);
      }
    };
    fetchStocks();
  }, []);

  useEffect(() => {
    if (activeTab > 0 && !analyticsData && !analyticsLoading) {
      const fetchAnalytics = async () => {
        setAnalyticsLoading(true);
        try {
          const res = await fetch('/api/analytics');
          const data = await res.json();
          setAnalyticsData(data);
        } catch (e) {
          console.error('Error fetching analytics:', e);
        } finally {
          setAnalyticsLoading(false);
        }
      };
      fetchAnalytics();
    }
  }, [activeTab, analyticsData, analyticsLoading]);

  const handleToggle = (ticker) => {
    setSelectedTickers(prev =>
      prev.includes(ticker) ? prev.filter(t => t !== ticker) : [...prev, ticker]
    );
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>

      {/* Sidebar */}
      <Box sx={{
        width: '220px',
        flexShrink: 0,
        minHeight: '100vh',
        backgroundColor: '#111318',
        borderRight: '1px solid #1f2530',
        p: 3,
      }}>
        <Typography sx={{
          color: '#c8f060',
          fontWeight: 700,
          fontSize: '1.1rem',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          letterSpacing: -0.3,
        }}>
          <span>↗</span> BursaView AI
        </Typography>
        <Typography sx={{
          color: '#6b7280',
          fontSize: '0.6rem',
          letterSpacing: 1.5,
          mt: 0.5,
          display: 'block',
          textTransform: 'uppercase',
        }}>
          Capstone Artifact V1.0
        </Typography>

        <Typography sx={{
          display: 'block',
          mt: 4, mb: 1,
          color: '#6b7280',
          fontSize: '0.6rem',
          fontWeight: 700,
          letterSpacing: 1.5,
          textTransform: 'uppercase',
        }}>
          Select Stocks
        </Typography>

        <FormGroup>
          {stocks.map(stock => (
            <FormControlLabel
              key={stock.ticker}
              control={
                <Checkbox
                  checked={selectedTickers.includes(stock.ticker)}
                  onChange={() => handleToggle(stock.ticker)}
                  size="small"
                />
              }
              label={
                <Typography sx={{ fontSize: '0.78rem', color: '#e8eaf0' }}>
                  {stock.name}
                </Typography>
              }
            />
          ))}
        </FormGroup>
      </Box>

      {/* Main content */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>

        {/* Top tab bar */}
        <Box sx={{
          backgroundColor: '#111318',
          borderBottom: '1px solid #1f2530',
          px: 3,
        }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            {TABS.map(label => <Tab key={label} label={label} />)}
          </Tabs>
        </Box>

        {/* Tab content */}
        <Box sx={{ flexGrow: 1 }}>
          {activeTab === 0 && <PredictionsTab stocks={stocks} selectedTickers={selectedTickers} />}
          {activeTab === 1 && <OverviewTab data={analyticsData} loading={analyticsLoading} stocks={stocks} />}
          {activeTab === 2 && <PriceTab data={analyticsData} loading={analyticsLoading} />}
          {activeTab === 3 && <VolumeTab data={analyticsData} loading={analyticsLoading} />}
          {activeTab === 4 && <StatsTab data={analyticsData} loading={analyticsLoading} />}
          {activeTab === 5 && <CorrelationTab data={analyticsData} loading={analyticsLoading} stocks={stocks} />}
        </Box>

      </Box>
    </Box>
  );
}

export default App;
