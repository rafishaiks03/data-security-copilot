export default function AuditLogs() {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Security Audit Logs</h1>
          <p>Trace security-sensitive operations and decisions.</p>
        </div>
      </div>

      <section className="panel">
        <div className="empty-state">
          Audit events will be connected to the API next.
        </div>
      </section>
    </div>
  );
}
