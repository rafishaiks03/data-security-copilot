export default function Dashboard() {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Security Operations</h1>
          <p>
            Monitor fraud detection, investigations, and security activity.
          </p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <span>Total Alerts</span>
          <strong>—</strong>
        </div>

        <div className="stat-card">
          <span>High Risk</span>
          <strong>—</strong>
        </div>

        <div className="stat-card">
          <span>Open Investigations</span>
          <strong>—</strong>
        </div>

        <div className="stat-card">
          <span>Agent Decisions</span>
          <strong>—</strong>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Recent Alerts</h2>
            <span className="panel-meta">Live API</span>
          </div>

          <div className="empty-state">
            Alert data will be connected next.
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Agent Activity</h2>
            <span className="panel-meta">Agentic Layer</span>
          </div>

          <div className="empty-state">
            Agent telemetry will appear here.
          </div>
        </section>
      </div>
    </div>
  );
}