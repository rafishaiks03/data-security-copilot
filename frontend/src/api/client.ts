const API_BASE_URL = "http://127.0.0.1:8000";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();

  const headers = new Headers(options.headers);

  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const text = await response.text();

    throw new Error(
      `API request failed (${response.status}): ${text || response.statusText}`,
    );
  }

  return response.json();
}

export interface Alert {
  alert_id: string;
  transaction_id: string;
  customer_id: string;
  alert_type: string;
  risk_score: string;
  risk_level: string;
  model_name: string;
  model_version: string;
  reason: string;
  features: Record<string, number>;
  status: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertListResponse {
  count: number;
  alerts: Alert[];
}

export interface AuditLog {
  audit_id: string;
  user_id: string | null;
  username: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  count: number;
  audit_logs: AuditLog[];
}

export function getAlerts(limit = 10) {
  return apiFetch<AlertListResponse>(
    `/api/v1/alerts?limit=${limit}`,
  );
}

export function getAuditLogs(limit = 50) {
  return apiFetch<AuditLogListResponse>(
    `/api/v1/audit-logs?limit=${limit}`,
  );
}