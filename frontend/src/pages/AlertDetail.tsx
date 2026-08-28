import {
  useEffect,
  useState,
} from "react";

import {
  ArrowLeft,
  CheckCircle,
  Clock,
  ShieldAlert,
} from "lucide-react";

import {
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getAlert,
  type Alert,
} from "../api/client";

export default function AlertDetail() {
  const navigate = useNavigate();

  const { alertId } = useParams<{
    alertId: string;
  }>();

  const [alert, setAlert] =
    useState<Alert | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    if (!alertId) {
      setError("Alert ID is missing.");
      setLoading(false);
      return;
    }

    async function loadAlert(alertId: string) {
      try {
        setLoading(true);
        setError(null);

        const response =
          await getAlert(alertId);

        setAlert(response);
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load alert.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadAlert(alertId);
  }, [alertId]);

  if (loading) {
    return (
      <div className="empty-state">
        Loading alert...
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div>
        <div className="page-header">
          <div>
            <h1>Alert</h1>

            <p>
              Unable to load the requested
              fraud alert.
            </p>
          </div>
        </div>

        <section className="panel">
          <div className="login-error">
            {error ??
              "Alert could not be found."}
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              navigate("/alerts")
            }
            style={{
              marginTop: "15px",
            }}
          >
            <ArrowLeft size={16} />
            Back to alerts
          </button>
        </section>
      </div>
    );
  }

  const riskPercentage =
    Number(alert.risk_score) * 100;

  return (
    <div>
      <div className="page-header">
        <div>
          <button
            type="button"
            className="secondary-button"
            onClick={() =>
              navigate("/alerts")
            }
            style={{
              marginBottom: "14px",
            }}
          >
            <ArrowLeft size={16} />
            Back to alerts
          </button>

          <h1>Fraud Alert</h1>

          <p>
            Investigation details for{" "}
            <strong>
              {alert.alert_id}
            </strong>
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Risk Score
            </span>

            <div className="stat-icon">
              <ShieldAlert size={19} />
            </div>
          </div>

          <div className="stat-value">
            {riskPercentage.toFixed(2)}%
          </div>

          <div className="stat-change">
            {alert.risk_level}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Status
            </span>

            <div className="stat-icon">
              <CheckCircle size={19} />
            </div>
          </div>

          <div className="stat-value">
            {alert.status}
          </div>

          <div className="stat-change">
            Current state
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Model
            </span>
          </div>

          <div
            className="stat-value"
            style={{
              fontSize: "18px",
            }}
          >
            {alert.model_name}
          </div>

          <div className="stat-change">
            Version {alert.model_version}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span className="stat-label">
              Created
            </span>

            <div className="stat-icon">
              <Clock size={19} />
            </div>
          </div>

          <div
            className="stat-value"
            style={{
              fontSize: "15px",
            }}
          >
            {new Date(
              alert.created_at,
            ).toLocaleDateString()}
          </div>

          <div className="stat-change">
            {new Date(
              alert.created_at,
            ).toLocaleTimeString()}
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Detection</h2>

              <p>
                Core fraud detection information
              </p>
            </div>
          </div>

          <div className="control-list">
            <div className="control-row">
              <span>Alert Type</span>
              <strong>
                {alert.alert_type}
              </strong>
            </div>

            <div className="control-row">
              <span>Transaction ID</span>
              <strong>
                {alert.transaction_id}
              </strong>
            </div>

            <div className="control-row">
              <span>Customer ID</span>
              <strong>
                {alert.customer_id}
              </strong>
            </div>

            <div className="control-row">
              <span>Risk Level</span>
              <strong>
                {alert.risk_level}
              </strong>
            </div>

            <div className="control-row">
              <span>Model</span>
              <strong>
                {alert.model_name}
              </strong>
            </div>

            <div className="control-row">
              <span>Model Version</span>
              <strong>
                {alert.model_version}
              </strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Detection Reason</h2>

              <p>
                Explanation returned by the
                detection service
              </p>
            </div>
          </div>

          <div
            style={{
              color: "#b9c7d6",
              lineHeight: 1.7,
              fontSize: "14px",
            }}
          >
            {alert.reason ||
              "No explanation was provided."}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Model Features</h2>

            <p>
              Features supplied to the fraud
              detection model
            </p>
          </div>
        </div>

        <pre
          style={{
            margin: 0,
            padding: "16px",
            overflowX: "auto",
            borderRadius: "8px",
            background: "#071321",
            border: "1px solid #172b40",
            color: "#b9c7d6",
            fontSize: "12px",
          }}
        >
          {JSON.stringify(
            alert.features,
            null,
            2,
          )}
        </pre>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Review Information</h2>

            <p>
              Alert investigation metadata
            </p>
          </div>
        </div>

        <div className="control-list">
          <div className="control-row">
            <span>Reviewed By</span>

            <strong>
              {alert.reviewed_by ??
                "Not reviewed"}
            </strong>
          </div>

          <div className="control-row">
            <span>Reviewed At</span>

            <strong>
              {alert.reviewed_at
                ? new Date(
                    alert.reviewed_at,
                  ).toLocaleString()
                : "Not reviewed"}
            </strong>
          </div>

          <div className="control-row">
            <span>Updated</span>

            <strong>
              {new Date(
                alert.updated_at,
              ).toLocaleString()}
            </strong>
          </div>
        </div>
      </section>
    </div>
  );
}