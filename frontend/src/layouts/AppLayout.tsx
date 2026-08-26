import { NavLink, Outlet } from "react-router-dom";
import {
  Activity,
  Bot,
  Database,
  FileSearch,
  LayoutDashboard,
  Shield,
  Terminal,
  Users,
} from "lucide-react";

const navigation = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/alerts", label: "Fraud Alerts", icon: Shield },
  { to: "/agents", label: "Agent Console", icon: Bot },
  { to: "/sql", label: "SQL Playground", icon: Terminal },
  { to: "/data", label: "Data Explorer", icon: Database },
  { to: "/audit-logs", label: "Audit Logs", icon: FileSearch },
  { to: "/users", label: "Users & Roles", icon: Users },
];

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Activity size={20} />
          </div>
          <div>
            <div className="brand-name">Security Copilot</div>
            <div className="brand-subtitle">AI Security Platform</div>
          </div>
        </div>

        <nav className="navigation">
          <div className="nav-section">OPERATIONS</div>

          {navigation.slice(0, 2).map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}

          <div className="nav-section">AI PLATFORM</div>

          {navigation.slice(2, 5).map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}

          <div className="nav-section">GOVERNANCE</div>

          {navigation.slice(5).map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `nav-item ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot" />
            <span>All systems operational</span>
          </div>

          <div className="user-card">
            <div className="avatar">A</div>
            <div>
              <div className="user-name">admin</div>
              <div className="user-role">SECURITY_ADMIN</div>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="topbar-title">Data & Security Copilot</div>
            <div className="topbar-subtitle">
              AI-powered security operations
            </div>
          </div>

          <div className="topbar-right">
            <div className="live-indicator">
              <span className="status-dot" />
              LIVE
            </div>
            <div className="environment">LOCAL</div>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}
