import type React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  CheckCircle,
  Plus,
  RefreshCw,
  ShieldAlert,
  UserRound,
  X,
} from "lucide-react";

import { createUser, getUsers, updateUser, type User } from "../api/client";

const ROLES = ["SECURITY_ADMIN", "SECURITY_ANALYST", "AUDITOR"];

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [showCreate, setShowCreate] = useState(false);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("AUDITOR");

  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function loadUsers() {
    try {
      setLoading(true);
      setError(null);

      const response = await getUsers();

      setUsers(response.users);
    } catch (err) {
      console.error(err);

      setError(err instanceof Error ? err.message : "Unable to load users.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    const query = search.trim().toLowerCase();

    return users.filter((user) => {
      const matchesSearch =
        !query ||
        user.username.toLowerCase().includes(query) ||
        user.user_id.toLowerCase().includes(query);

      const matchesRole = roleFilter === "ALL" || user.role === roleFilter;

      const matchesStatus =
        statusFilter === "ALL" ||
        (statusFilter === "ACTIVE" && user.is_active) ||
        (statusFilter === "INACTIVE" && !user.is_active);

      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [users, search, roleFilter, statusFilter]);

  async function handleCreateUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setCreating(true);
      setCreateError(null);

      await createUser({
        username: username.trim(),
        password,
        role,
      });

      setUsername("");
      setPassword("");
      setRole("AUDITOR");
      setShowCreate(false);

      await loadUsers();
    } catch (err) {
      console.error(err);

      setCreateError(
        err instanceof Error ? err.message : "Unable to create user.",
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleRoleChange(user: User, newRole: string) {
    if (user.role === newRole) {
      return;
    }

    try {
      setUpdatingUserId(user.user_id);
      setActionError(null);
      setSuccessMessage(null);

      const updatedUser = await updateUser(user.user_id, {
        role: newRole,
      });

      setUsers((currentUsers) =>
        currentUsers.map((currentUser) =>
          currentUser.user_id === updatedUser.user_id
            ? updatedUser
            : currentUser,
        ),
      );

      setSuccessMessage(
        `Role for "${updatedUser.username}" updated to ${updatedUser.role}.`,
      );
    } catch (err) {
      console.error(err);

      setActionError(
        err instanceof Error ? err.message : "Unable to update user role.",
      );
    } finally {
      setUpdatingUserId(null);
    }
  }

  async function handleStatusChange(user: User) {
    const newStatus = !user.is_active;

    try {
      setUpdatingUserId(user.user_id);
      setActionError(null);
      setSuccessMessage(null);

      const updatedUser = await updateUser(user.user_id, {
        is_active: newStatus,
      });

      setUsers((currentUsers) =>
        currentUsers.map((currentUser) =>
          currentUser.user_id === updatedUser.user_id
            ? updatedUser
            : currentUser,
        ),
      );

      setSuccessMessage(
        `"${updatedUser.username}" is now ${
          updatedUser.is_active ? "active" : "inactive"
        }.`,
      );
    } catch (err) {
      console.error(err);

      setActionError(
        err instanceof Error ? err.message : "Unable to update user status.",
      );
    } finally {
      setUpdatingUserId(null);
    }
  }

  function closeCreateModal() {
    if (creating) {
      return;
    }

    setShowCreate(false);
    setCreateError(null);
    setUsername("");
    setPassword("");
    setRole("AUDITOR");
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Users & Roles</h1>

          <p>Manage application users and security roles.</p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "8px",
          }}
        >
          <button
            type="button"
            className="secondary-button"
            onClick={loadUsers}
            disabled={loading}
          >
            <RefreshCw size={15} />

            {loading ? "Refreshing..." : "Refresh"}
          </button>

          <button
            type="button"
            className="login-button"
            style={{
              height: "38px",
              padding: "0 14px",
              marginTop: 0,
            }}
            onClick={() => {
              setCreateError(null);
              setShowCreate(true);
            }}
          >
            <Plus size={15} />
            Create User
          </button>
        </div>
      </div>
      {successMessage && (
        <div
          className="panel"
          style={{
            marginBottom: "16px",
            borderColor: "#285c45",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "9px",
              color: "#76d7a7",
            }}
          >
            <CheckCircle size={18} />
            <strong>{successMessage}</strong>
          </div>
        </div>
      )}

      {actionError && (
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
              gap: "9px",
              color: "#ff8b8b",
            }}
          >
            <ShieldAlert size={18} />
            <strong>{actionError}</strong>
          </div>
        </div>
      )}
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
              gap: "9px",
            }}
          >
            <ShieldAlert size={18} />

            <strong>Unable to load users</strong>
          </div>

          <p style={{ color: "#aebdcd" }}>{error}</p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadUsers}
          >
            Retry
          </button>
        </div>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Application Users</h2>

            <p>
              {loading
                ? "Loading users..."
                : `${filteredUsers.length} user${
                    filteredUsers.length === 1 ? "" : "s"
                  } shown`}
            </p>
          </div>

          <span className="panel-status">SECURITY ADMIN</span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(220px, 1fr) 190px 170px",
            gap: "10px",
            marginBottom: "18px",
          }}
        >
          <input
            type="search"
            placeholder="Search username or user ID..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            style={inputStyle}
          />

          <select
            value={roleFilter}
            onChange={(event) => setRoleFilter(event.target.value)}
            style={inputStyle}
          >
            <option value="ALL">All roles</option>

            {ROLES.map((roleName) => (
              <option key={roleName} value={roleName}>
                {roleName}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            style={inputStyle}
          >
            <option value="ALL">All statuses</option>

            <option value="ACTIVE">Active</option>

            <option value="INACTIVE">Inactive</option>
          </select>
        </div>

        {loading && <div className="empty-state">Loading users...</div>}

        {!loading && !error && filteredUsers.length === 0 && (
          <div className="empty-state">
            <UserRound size={24} />

            <div style={{ marginTop: "8px" }}>
              No users match the current filters.
            </div>
          </div>
        )}

        {!loading && filteredUsers.length > 0 && (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                minWidth: "850px",
              }}
            >
              <thead>
                <tr>
                  <th style={tableHeaderStyle}>User</th>

                  <th style={tableHeaderStyle}>Role</th>

                  <th style={tableHeaderStyle}>Status</th>

                  <th style={tableHeaderStyle}>Created</th>

                  <th style={tableHeaderStyle}>Updated</th>
                </tr>
              </thead>

              <tbody>
                {filteredUsers.map((user) => (
                  <tr
                    key={user.user_id}
                    style={{
                      borderTop: "1px solid #172b40",
                    }}
                  >
                    <td style={tableCellStyle}>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                        }}
                      >
                        <div
                          style={{
                            width: "32px",
                            height: "32px",
                            borderRadius: "8px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "#102238",
                            border: "1px solid #29415d",
                          }}
                        >
                          <UserRound size={16} />
                        </div>

                        <div
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "3px",
                          }}
                        >
                          <strong>{user.username}</strong>

                          <span
                            style={{
                              fontSize: "10px",
                              color: "#71859c",
                              fontFamily:
                                "ui-monospace, SFMono-Regular, Menlo, monospace",
                            }}
                          >
                            {user.user_id}
                          </span>
                        </div>
                      </div>
                    </td>

                    <td style={tableCellStyle}>
                      <select
                        value={user.role}
                        disabled={updatingUserId === user.user_id}
                        onChange={(event) =>
                          void handleRoleChange(user, event.target.value)
                        }
                        style={{
                          height: "32px",
                          padding: "0 8px",
                          borderRadius: "6px",
                          border: "1px solid #263c55",
                          background: "#071321",
                          color: "#edf5fc",
                          fontSize: "12px",
                          cursor:
                            updatingUserId === user.user_id
                              ? "wait"
                              : "pointer",
                          opacity: updatingUserId === user.user_id ? 0.6 : 1,
                        }}
                      >
                        {ROLES.map((roleName) => (
                          <option key={roleName} value={roleName}>
                            {roleName}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td style={tableCellStyle}>
                      <button
                        type="button"
                        onClick={() => void handleStatusChange(user)}
                        disabled={updatingUserId === user.user_id}
                        title={
                          user.is_active
                            ? "Click to deactivate"
                            : "Click to activate"
                        }
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "6px",
                          padding: "6px 9px",
                          borderRadius: "6px",
                          border: "1px solid #263c55",
                          background: "transparent",
                          color: user.is_active ? "#76d7a7" : "#8b9caf",
                          fontSize: "12px",
                          fontWeight: 600,
                          cursor:
                            updatingUserId === user.user_id
                              ? "wait"
                              : "pointer",
                          opacity: updatingUserId === user.user_id ? 0.6 : 1,
                        }}
                      >
                        {user.is_active ? (
                          <>
                            <CheckCircle size={14} />
                            ACTIVE
                          </>
                        ) : (
                          "INACTIVE"
                        )}
                      </button>
                    </td>

                    <td
                      style={{
                        ...tableCellStyle,
                        color: "#8fa2b6",
                      }}
                    >
                      {formatDate(user.created_at)}
                    </td>

                    <td
                      style={{
                        ...tableCellStyle,
                        color: "#8fa2b6",
                      }}
                    >
                      {formatDate(user.updated_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {showCreate && (
        <div
          style={modalBackdropStyle}
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeCreateModal();
            }
          }}
        >
          <div style={modalStyle}>
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                marginBottom: "24px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: 0,
                  }}
                >
                  Create User
                </h2>

                <p
                  style={{
                    margin: "7px 0 0",
                    color: "#8093a8",
                    fontSize: "13px",
                  }}
                >
                  Create a new application user.
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={closeCreateModal}
                disabled={creating}
              >
                <X size={17} />
              </button>
            </div>

            {createError && (
              <div
                className="login-error"
                style={{
                  marginBottom: "16px",
                }}
              >
                <strong>User creation failed</strong>

                <span>{createError}</span>
              </div>
            )}

            <form
              onSubmit={handleCreateUser}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "17px",
              }}
            >
              <div className="form-field">
                <label htmlFor="new-username">Username</label>

                <input
                  id="new-username"
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  minLength={3}
                  maxLength={100}
                  autoComplete="off"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="new-password">Password</label>

                <input
                  id="new-password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={8}
                  maxLength={72}
                  autoComplete="new-password"
                  required
                />

                <span
                  style={{
                    color: "#71859c",
                    fontSize: "10px",
                    marginTop: "4px",
                  }}
                >
                  8–72 characters
                </span>
              </div>

              <div className="form-field">
                <label htmlFor="new-role">Role</label>

                <select
                  id="new-role"
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                  style={{
                    height: "44px",
                    padding: "0 11px",
                    borderRadius: "7px",
                    border: "1px solid #263c55",
                    background: "#071321",
                    color: "#edf5fc",
                  }}
                >
                  {ROLES.map((roleName) => (
                    <option key={roleName} value={roleName}>
                      {roleName}
                    </option>
                  ))}
                </select>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "9px",
                  marginTop: "6px",
                }}
              >
                <button
                  type="button"
                  className="secondary-button"
                  onClick={closeCreateModal}
                  disabled={creating}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="login-button"
                  style={{
                    height: "40px",
                    padding: "0 16px",
                    marginTop: 0,
                  }}
                  disabled={creating}
                >
                  {creating ? "Creating..." : "Create User"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function formatDate(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  height: "42px",
  padding: "0 12px",
  borderRadius: "7px",
  border: "1px solid #263c55",
  background: "#071321",
  color: "#edf5fc",
  outline: "none",
};

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
};

const modalBackdropStyle: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 100,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "20px",
  background: "rgba(2, 8, 15, 0.72)",
  backdropFilter: "blur(5px)",
};

const modalStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: "460px",
  padding: "28px",
  borderRadius: "14px",
  border: "1px solid #263c55",
  background: "#0a1626",
  boxShadow: "0 30px 90px rgba(0, 0, 0, 0.5)",
};
