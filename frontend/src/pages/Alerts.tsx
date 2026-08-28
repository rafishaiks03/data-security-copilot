import type React from "react";
import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Eye, RefreshCw, ShieldAlert } from "lucide-react";
import { useNavigate } from "react-router-dom";

import {
  getAlerts,
  type Alert,
} from "../api/client";

export default function Alerts() {
  const navigate = useNavigate();

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  async function loadAlerts() {
    try {
      setLoading(true);
      setError(null);

      const response = await getAlerts(100);

      setAlerts(response.alerts);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load fraud alerts.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  const filteredAlerts = useMemo(() => {
    const query = search.trim().toLowerCase();

    return alerts.filter((alert) => {
      const matchesSearch =
        !query ||
        alert.alert_id.toLowerCase().includes(query) ||
        alert.transaction_id.toLowerCase().includes(query) ||
        alert.customer_id.toLowerCase().includes(query) ||
        alert.alert_type.toLowerCase().includes(query);

      const matchesRisk =
        riskFilter === "ALL" ||
        alert.risk_level === riskFilter;

      const matchesStatus =
        statusFilter === "ALL" ||
        alert.status === statusFilter;

      return matchesSearch && matchesRisk && matchesStatus;
    });
  }, [alerts, search, riskFilter, statusFilter]);

  function getRiskClass(riskLevel: string) {
    switch (riskLevel) {
      case "CRITICAL":
        return "alert-risk critical";

      case "HIGH":
        return "alert-risk high";

      case "MEDIUM":
        return "alert-risk medium";

      case "LOW":
        return "alert-risk low";

      default:
        return "alert-risk";
    }
  }

  function getStatusClass(status: string) {
    switch (status) {
      case "OPEN":
        return "alert-status open";

      case "CLOSED":
        return "alert-status closed";

      case "REVIEWED":
        return "alert-status reviewed";

      default:
        return "alert-status";
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Fraud Alerts</h1>

          <p>
            Review and investigate ML-generated security alerts.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={loadAlerts}
          disabled={loading}
        >
          <RefreshCw size={15} />

          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div
          className="panel"
          style={{
            marginBottom: "16px",
            borderColor: "#6b3030",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <AlertTriangle size={18} />

            <strong>Unable to load alerts</strong>
          </div>

          <p style={{ color: "#aebdcd" }}>
            {error}
          </p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadAlerts}
          >
            Retry
          </button>
        </div>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Alert Queue</h2>

            <p>
              {loading
                ? "Loading alerts..."
                : `${filteredAlerts.length} alert${
                    filteredAlerts.length === 1 ? "" : "s"
                  } shown`}
            </p>
          </div>

          <div className="panel-status">
            LIVE API
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(220px, 1fr) 160px 160px",
            gap: "10px",
            marginBottom: "18px",
          }}
        >
          <input
            type="search"
            placeholder="Search alerts, transactions, customers..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "10px 12px",
              borderRadius: "7px",
              border: "1px solid #263c55",
              background: "#071321",
              color: "#edf5fc",
              outline: "none",
            }}
          />

          <select
            value={riskFilter}
            onChange={(event) =>
              setRiskFilter(event.target.value)
            }
            style={{
              padding: "10px 12px",
              borderRadius: "7px",
              border: "1px solid #263c55",
              background: "#071321",
              color: "#edf5fc",
              outline: "none",
            }}
          >
            <option value="ALL">All risk levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value)
            }
            style={{
              padding: "10px 12px",
              borderRadius: "7px",
              border: "1px solid #263c55",
              background: "#071321",
              color: "#edf5fc",
              outline: "none",
            }}
          >
            <option value="ALL">All statuses</option>
            <option value="OPEN">Open</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>

        {loading && (
          <div className="empty-state">
            Loading fraud alerts...
          </div>
        )}

        {!loading && !error && filteredAlerts.length === 0 && (
          <div className="empty-state">
            <ShieldAlert size={24} />

            <div style={{ marginTop: "8px" }}>
              No alerts match the current filters.
            </div>
          </div>
        )}

        {!loading && filteredAlerts.length > 0 && (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                minWidth: "900px",
              }}
            >
              <thead>
                <tr>
                  <th style={tableHeaderStyle}>
                    Alert
                  </th>

                  <th style={tableHeaderStyle}>
                    Risk
                  </th>

                  <th style={tableHeaderStyle}>
                    Score
                  </th>

                  <th style={tableHeaderStyle}>
                    Transaction
                  </th>

                  <th style={tableHeaderStyle}>
                    Customer
                  </th>

                  <th style={tableHeaderStyle}>
                    Model
                  </th>

                  <th style={tableHeaderStyle}>
                    Status
                  </th>

                  <th style={tableHeaderStyle}>
                    Action
                  </th>
                </tr>
              </thead>

              <tbody>
                {filteredAlerts.map((alert) => (
                  <tr
                    key={alert.alert_id}
                    onClick={() =>
                      navigate(`/alerts/${alert.alert_id}`)
                    }
                    style={{
                      cursor: "pointer",
                      borderTop: "1px solid #172b40",
                    }}
                  >
                    <td style={tableCellStyle}>
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "4px",
                        }}
                      >
                        <strong>
                          {alert.alert_type}
                        </strong>

                        <span
                          style={{
                            fontSize: "11px",
                            color: "#71859c",
                          }}
                        >
                          {alert.alert_id.slice(0, 12)}
                        </span>
                      </div>
                    </td>

                    <td style={tableCellStyle}>
                      <span className={getRiskClass(alert.risk_level)}>
                        {alert.risk_level}
                      </span>
                    </td>

                    <td style={tableCellStyle}>
                      <strong>
                        {(
                          Number(alert.risk_score) * 100
                        ).toFixed(2)}
                        %
                      </strong>
                    </td>

                    <td style={tableCellStyle}>
                      <span
                        style={{
                          fontFamily:
                            "ui-monospace, SFMono-Regular, Menlo, monospace",
                          fontSize: "12px",
                        }}
                      >
                        {alert.transaction_id.slice(0, 12)}
                      </span>
                    </td>

                    <td style={tableCellStyle}>
                      {alert.customer_id.slice(0, 12)}
                    </td>

                    <td style={tableCellStyle}>
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "3px",
                        }}
                      >
                        <span>
                          {alert.model_name}
                        </span>

                        <span
                          style={{
                            fontSize: "11px",
                            color: "#71859c",
                          }}
                        >
                          v{alert.model_version}
                        </span>
                      </div>
                    </td>

                    <td style={tableCellStyle}>
                      <span className={getStatusClass(alert.status)}>
                        {alert.status}
                      </span>
                    </td>

                    <td style={tableCellStyle}>
                      <button
                        type="button"
                        className="icon-button"
                        title="View alert"
                        onClick={(event) => {
                          event.stopPropagation();

                          navigate(
                            `/alerts/${alert.alert_id}`,
                          );
                        }}
                      >
                        <Eye size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

const tableHeaderStyle: React.CSSProperties = {
  padding: "11px 12px",
  textAlign: "left",
  color: "#71859c",
  fontSize: "11px",
  fontWeight: 600,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
  whiteSpace: "nowrap",
};

const tableCellStyle: React.CSSProperties = {
  padding: "14px 12px",
  color: "#dce7f4",
  fontSize: "13px",
  verticalAlign: "middle",
  whiteSpace: "nowrap",
};