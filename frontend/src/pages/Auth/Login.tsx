import { useState } from "react";
import type { FormEvent } from "react";
import { useAuth } from "../../auth/AuthContext";
import {
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Activity,
  LockKeyhole,
  ShieldCheck,
  User,
} from "lucide-react";

import {login} from "../../api/client";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { refreshAuth } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      await login(username, password);

      refreshAuth();

      const state = location.state as
        | { from?: { pathname?: string } }
        | null;

      const from = state?.from?.pathname ?? "/dashboard";

      navigate(from, { replace: true });
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to sign in.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="login-glow login-glow-one" />
        <div className="login-glow login-glow-two" />
      </div>

      <div className="login-container">
        <div className="login-card">

          <div className="login-brand">
            <div className="login-brand-mark">
              <Activity size={21} />
            </div>

            <div>
              <div className="login-brand-name">
                Security Copilot
              </div>

              <div className="login-brand-subtitle">
                AI Security Platform
              </div>
            </div>
          </div>

          <div className="login-heading">
            <div className="login-shield">
              <ShieldCheck size={21} />
            </div>

            <div>
              <h1>Sign in</h1>

              <p>
                Authenticate to access security operations.
              </p>
            </div>
          </div>

          {error && (
            <div className="login-error">
              <strong>Authentication failed</strong>
              <span>{error}</span>
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="login-form"
          >
            <div className="login-field">
              <label htmlFor="username">
                Username
              </label>

              <div className="login-input-wrapper">
                <User size={17} />

                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(event) =>
                    setUsername(event.target.value)
                  }
                  autoComplete="username"
                  placeholder="Enter your username"
                  required
                />
              </div>
            </div>

            <div className="login-field">
              <label htmlFor="password">
                Password
              </label>

              <div className="login-input-wrapper">
                <LockKeyhole size={17} />

                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="login-spinner" />
                  Signing in...
                </>
              ) : (
                <>
                  <ShieldCheck size={17} />
                  Sign in
                </>
              )}
            </button>
          </form>

          <div className="login-security">
            <ShieldCheck size={14} />
            Secure authentication enabled
          </div>
        </div>

        <div className="login-footer">
          <span>DATA & SECURITY COPILOT</span>
          <span>LOCAL ENVIRONMENT</span>
        </div>
      </div>
    </div>
  );
}
