import StatCard from '../components/StatCard';

export default function Dashboard() {
  return (
    <div className="page">
      <h1>Dashboard</h1>
      <div className="stats-grid">
        <StatCard title="Total Farms" value="128" subtitle="Across all counties" />
        <StatCard title="Yield Forecast" value="5.8 t/ha" subtitle="This season" />
        <StatCard title="Alerts" value="12" subtitle="Needs review" />
      </div>
    </div>
  );
}
