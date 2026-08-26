export default function SQLPlayground() {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>SQL Playground</h1>
          <p>
            Investigate security data through a controlled,
            read-only SQL interface.
          </p>
        </div>

        <div className="security-badge">
          READ ONLY
        </div>
      </div>

      <section className="sql-workspace">
        <div className="panel sql-editor">
          <div className="panel-header">
            <h2>Query Editor</h2>
            <span className="panel-meta">PostgreSQL</span>
          </div>

          <textarea
            className="sql-input"
            defaultValue={`SELECT
    alert_type,
    risk_level,
    COUNT(*) AS alert_count
FROM fraud_alerts
GROUP BY alert_type, risk_level
ORDER BY alert_count DESC;`}
          />

          <div className="editor-actions">
            <button className="primary-button">
              Run Query
            </button>

            <button className="secondary-button">
              Format
            </button>

            <button className="secondary-button">
              Clear
            </button>
          </div>
        </div>

        <div className="panel schema-panel">
          <div className="panel-header">
            <h2>Schema</h2>
          </div>

          <div className="schema-list">
            <div>▾ banking</div>
            <div>├─ fraud_alerts</div>
            <div>├─ transactions</div>
            <div>├─ customers</div>
            <div>├─ users</div>
            <div>└─ audit_logs</div>
          </div>
        </div>
      </section>

      <section className="panel results-panel">
        <div className="panel-header">
          <h2>Query Results</h2>
          <span className="panel-meta">
            No query executed
          </span>
        </div>

        <div className="empty-state">
          Run a query to view results.
        </div>
      </section>
    </div>
  );
}