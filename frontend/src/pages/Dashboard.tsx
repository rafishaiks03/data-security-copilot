import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Bot,
  CheckCircle,
  Database,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";


import {
  getAlerts,
  getAuditLogs,
  type Alert,
  type AuditLog,
} from "../api/client";

export default function Dashboard() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError(null);

      const [alertResponse, auditResponse] = await Promise.all([
        getAlerts(10),
        getAuditLogs(50),
      ]);

      setAlerts(alertResponse.alerts);
      setAuditLogs(auditResponse.audit_logs);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load dashboard data.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const activeAlerts = useMemo(
    () => alerts.filter((alert) => alert.status === "OPEN").length,
    [alerts],
  );

  const highRiskAlerts = useMemo(
    () =>
      alerts.filter(
        (alert) =>
          alert.risk_level === "HIGH" ||
          alert.risk_level === "CRITICAL",
      ).length,
    [alerts],
  );

  const agentRuns = useMemo(
    () =>
      auditLogs.filter(
        (log) =>
          log.action.includes("AGENT") ||
          log.resource_type?.includes("AGENT"),
      ).length,
    [auditLogs],
  );

  const stats = [
    {
      label: "Active Fraud Alerts",
      value: loading ? "—" : activeAlerts,
      change: "Live API",
      icon: ShieldAlert,
    },
    {
      label: "High Risk Transactions",
      value: loading ? "—" : highRiskAlerts,
      change: "Current sample",
      icon: AlertTriangle,
    },
    {
      label: "Agent Activity",
      value: loading ? "—" : agentRuns,
      change: "Audit telemetry",
      icon: Bot,
    },
    {
      label: "Security Events",
      value: loading ? "—" : auditLogs.length,
      change: "Recent events",
      icon: Database,
    },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Security Operations</h1>

          <p>
            Monitor fraud detection, AI agents, data activity, and security
            controls.
          </p>
        </div>

        <div className="header-badge">
          <CheckCircle size={16} />
          Platform Operational
        </div>
      </div>

      {error && (
        <div
          className="panel"
          style={{
            marginBottom: "15px",
            borderColor: "#6b3030",
          }}
        >
          <strong>Dashboard API error</strong>

          <p style={{ color: "#aebdcd" }}>{error}</p>

          <button
            onClick={loadDashboard}
            style={{
              marginTop: "8px",
              padding: "8px 12px",
              borderRadius: "6px",
              border: "1px solid #29415d",
              background: "#102238",
              color: "#dce7f4",
              cursor: "pointer",
            }}
          >
            Retry
          </button>
        </div>
      )}

      <div className="stats-grid">
        {stats.map(({ label, value, change, icon: Icon }) => (
          <div className="stat-card" key={label}>
            <div className="stat-top">
              <span className="stat-label">{label}</span>

              <div className="stat-icon">
                <Icon size={19} />
              </div>
            </div>

            <div className="stat-value">{value}</div>

            <div className="stat-change">
              <TrendingUp size={14} />
              {change}
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="panel large-panel">
          <div className="panel-header">
            <div>
              <h2>Risk Activity</h2>

              <p>
                Recent fraud detection events from the production API
              </p>
            </div>

            <span className="panel-status">LIVE API</span>
          </div>

          <div className="chart-placeholder">
            <div className="chart-bars">
              {alerts.length > 0
                ? alerts.map((alert, index) => {
                    const score =
                      Number(alert.risk_score) * 100;

                    return (
                      <div
                        className="chart-column"
                        key={alert.alert_id}
                      >
                        <div
                          className="chart-bar"
                          style={{
                            height: `${Math.max(score, 8)}%`,
                          }}
                          title={`${score.toFixed(2)}% risk`}
                        />

                        <span>{index + 1}</span>
                      </div>
                    );
                  })
                : Array.from({ length: 10 }).map((_, index) => (
                    <div
                      className="chart-column"
                      key={index}
                    >
                      <div
                        className="chart-bar"
                        style={{ height: "8%" }}
                      />

                      <span>{index + 1}</span>
                    </div>
                  ))}
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>AI Agent Status</h2>

              <p>Agentic orchestration layer</p>
            </div>
          </div>

          <div className="agent-status">
            <div className="agent-row">
              <div className="agent-info">
                <span className="status-dot" />

                <span>Fraud Investigation Agent</span>
              </div>

              <span className="running">READY</span>
            </div>

            <div className="agent-row">
              <div className="agent-info">
                <span className="status-dot" />

                <span>Risk Analysis Agent</span>
              </div>

              <span className="running">READY</span>
            </div>

            <div className="agent-row">
              <div className="agent-info">
                <span className="status-dot" />

                <span>SQL Analysis Agent</span>
              </div>

              <span className="idle">READY</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>Recent Alerts</h2>

              <p>
                Live alerts from the fraud detection service
              </p>
            </div>
          </div>

          <div className="alert-list">
            {loading && (
              <div className="empty-state">
                Loading alerts...
              </div>
            )}

            {!loading && alerts.length === 0 && (
              <div className="empty-state">
                No fraud alerts found.
              </div>
            )}

            {alerts.slice(0, 5).map((alert) => (
              <div
                className="alert-row"
                key={alert.alert_id}
              >
                <div
                  className={`severity ${
                    alert.risk_level === "HIGH" ||
                    alert.risk_level === "CRITICAL"
                      ? "high"
                      : "medium"
                  }`}
                >
                  {alert.risk_level === "CRITICAL"
                    ? "CRIT"
                    : alert.risk_level === "HIGH"
                      ? "HIGH"
                      : "MED"}
                </div>

                <div className="alert-main">
                  <strong>
                    {alert.alert_type} detection
                  </strong>

                  <span>
                    Transaction #
                    {alert.transaction_id.slice(0, 8)}
                  </span>
                </div>

                <span className="alert-score">
                  {(Number(alert.risk_score) * 100).toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>Security Controls</h2>

              <p>Platform governance</p>
            </div>
          </div>

          <div className="control-list">
            <div className="control-row">
              <CheckCircle size={18} />

              <span>RBAC enforcement</span>

              <strong>ON</strong>
            </div>

            <div className="control-row">
              <CheckCircle size={18} />

              <span>Audit logging</span>

              <strong>ON</strong>
            </div>

            <div className="control-row">
              <CheckCircle size={18} />

              <span>Model monitoring</span>

              <strong>ON</strong>
            </div>

            <div className="control-row">
              <CheckCircle size={18} />

              <span>Agent guardrails</span>

              <strong>ON</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}