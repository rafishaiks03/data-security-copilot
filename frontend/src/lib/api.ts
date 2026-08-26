const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface FraudAlert {
  alert_id: string;
  transaction_id: string;
  customer_id: string;
  alert_type: string;
  risk_score: string | number;
  risk_level: string;
  model_name: string;
  model_version: string;
  reason: string;
  features: Record<string, unknown>;
  status: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertListResponse {
  count: number;
  alerts: FraudAlert[];
}

function getAccessToken(): string | null {
  return (
    localStorage.getItem("access_token") ??
    localStorage.getItem("token") ??
    sessionStorage.getItem("access_token") ??
    sessionStorage.getItem("token")
  );
}

async function apiFetch<T>(path: string): Promise<T> {
  const token = getAccessToken();

  const headers: HeadersInit = {
    Accept: "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers,
  });

  if (!response.ok) {
    let message = `API request failed (${response.status})`;

    try {
      const body = await response.json();
      if (body?.detail) {
        message = body.detail;
      }
    } catch {
      // Keep the default message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getAlerts(limit = 10): Promise<AlertListResponse> {
  return apiFetch<AlertListResponse>(
    `/api/v1/alerts?limit=${encodeURIComponent(limit)}`,
  );
}