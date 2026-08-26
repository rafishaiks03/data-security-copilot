import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import AlertDetail from "./pages/AlertDetail";
import AgentConsole from "./pages/AgentConsole";
import AgentRun from "./pages/AgentRun";
import SQLPlayground from "./pages/SQLPlayground";
import AuditLogs from "./pages/AuditLogs";
import Users from "./pages/Users";
import DataExplorer from "./pages/DataExplorer";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/alerts/:alertId" element={<AlertDetail />} />
          <Route path="/agents" element={<AgentConsole />} />
          <Route path="/agents/:runId" element={<AgentRun />} />
          <Route path="/sql" element={<SQLPlayground />} />
          <Route path="/audit-logs" element={<AuditLogs />} />
          <Route path="/users" element={<Users />} />
          <Route path="/data" element={<DataExplorer />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
