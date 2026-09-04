const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function getToken(): string | null {
  return (
    localStorage.getItem("access_token") ??
    sessionStorage.getItem("access_token")
  );
}

function saveToken(token: string): void {
  localStorage.setItem("access_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("access_token");
  sessionStorage.removeItem("access_token");
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();

  const headers = new Headers(options.headers);

  headers.set("Accept", "application/json");

  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
  clearToken();

  window.dispatchEvent(
    new Event("auth:logout"),
  );
}

  if (!response.ok) {
    let message = `API request failed (${response.status})`;

    try {
      const body = await response.json();

      if (body?.detail) {
        message = body.detail;
      }
    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  user_id: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  count: number;
  users: User[];
}

export interface UserCreateRequest {
  username: string;
  password: string;
  role: string;
}

export interface UserUpdateRequest {
  role?: string;
  is_active?: boolean;
}

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const response = await apiFetch<TokenResponse>(
    "/api/v1/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    },
  );

  saveToken(response.access_token);

  return response;
}

export interface Alert {
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
    `/api/v1/alerts?limit=${encodeURIComponent(limit)}`,
  );
}

export function getAlert(
  alertId: string,
): Promise<Alert> {
  return apiFetch<Alert>(
    `/api/v1/alerts/${encodeURIComponent(alertId)}`,
  );
}

export function getAuditLogs(limit = 50) {
  return apiFetch<AuditLogListResponse>(
    `/api/v1/audit-logs?limit=${encodeURIComponent(limit)}`,
  );
}

export function isAuthenticated(): boolean {
  return Boolean(getToken());
}

export function getUsers() {
  return apiFetch<UserListResponse>("/api/v1/users");
}

export function getUser(userId: string) {
  return apiFetch<User>(
    `/api/v1/users/${encodeURIComponent(userId)}`,
  );
}

export function createUser(
  request: UserCreateRequest,
) {
  return apiFetch<User>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function updateUser(
  userId: string,
  request: UserUpdateRequest,
) {
  return apiFetch<User>(
    `/api/v1/users/${encodeURIComponent(userId)}`,
    {
      method: "PATCH",
      body: JSON.stringify(request),
    },
  );
}