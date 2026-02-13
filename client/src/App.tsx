import { useState, useEffect, useCallback } from "react";
import ChatPanel from "./ChatPanel";
import Sidebar from "./Sidebar";
import { fetchHealth } from "./api";
import type { ModelMode, HealthResponse } from "./types";

export default function App() {
  const [mode, setMode] = useState<ModelMode>("quick");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const checkHealth = useCallback(async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
    } catch {
      setHealth({ status: "error", message: "Cannot reach backend" });
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return (
    <div className="app">
      {/* Mobile header */}
      <header className="mobile-header">
        <button
          className="hamburger"
          onClick={() => setSidebarOpen((o) => !o)}
          aria-label="Toggle sidebar"
        >
          <span />
          <span />
          <span />
        </button>
        <div className="mobile-brand">
          <span className="brand-dot" />
          cosmo
        </div>
      </header>

      <Sidebar
        mode={mode}
        onModeChange={setMode}
        health={health}
        onRefreshHealth={checkHealth}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      <main className="main">
        <ChatPanel mode={mode} />
      </main>
    </div>
  );
}
