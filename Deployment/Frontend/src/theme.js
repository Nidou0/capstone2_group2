export const PALETTE = [
  '#c8f060', '#60c8f0', '#f0906a', '#a78bfa', '#34d399',
  '#fb923c', '#f472b6', '#38bdf8', '#facc15', '#86efac'
];

export const C = {
  bg:       '#0a0c0f',
  surface:  '#111318',
  surface2: '#181c24',
  border:   '#1f2530',
  accent:   '#c8f060',
  text:     '#e8eaf0',
  muted:    '#6b7280',
  green:    '#4ade80',
  red:      '#f87171',
};

export const chartProps = {
  grid: { stroke: '#1f2530', strokeDasharray: '3 3' },
  axis: { tick: { fill: '#6b7280', fontSize: 10 }, axisLine: false, tickLine: false },
  tooltip: {
    contentStyle: {
      backgroundColor: '#181c24',
      border: '1px solid #1f2530',
      color: '#e8eaf0',
      borderRadius: 6,
      fontSize: 11,
    },
    cursor: { fill: 'rgba(255,255,255,0.03)' },
  },
  legend: { wrapperStyle: { fontSize: 11, color: '#6b7280' } },
};
