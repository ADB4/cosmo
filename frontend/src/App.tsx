import { useState, useEffect, useCallback } from "react";
import ChatPanel from "./pages/chat/ChatPanel";
import Apollo from "./pages/apollo/Apollo";
import { fetchHealth } from "./lib/api";
import type { ModelMode, HealthResponse } from "./lib/types";
import { MODE_INFO } from "./lib/types";

type Tab = "cosmo" | "apollo";

export default function App() {
  const [tab, setTab] = useState<Tab>("cosmo");
  const [mode, setMode] = useState<ModelMode>("qwen-7b");
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      setHealth(await fetchHealth());
    } catch {
      setHealth({ status: "error", message: "Cannot reach backend" });
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  const statusLabel =
    health?.status === "ok"
      ? "Ready"
      : health?.status === "error"
        ? "Offline"
        : "...";

  return (
    <div className="app">
      <div className="topbar">
        <span className="topbar-icon">{">_"}</span>

        <button
          className={`topbar-tab ${tab === "cosmo" ? "topbar-tab--active" : ""}`}
          onClick={() => setTab("cosmo")}
        >
          COSMO
        </button>
        <button
          className={`topbar-tab ${tab === "apollo" ? "topbar-tab--active" : ""}`}
          onClick={() => setTab("apollo")}
        >
          APOLLO
        </button>

        <span className="topbar-status">
          <span
            className={`status-dot status-dot--${health?.status ?? "unknown"}`}
          />
          {statusLabel}
        </span>

        <span className="topbar-spacer" />

        {tab === "cosmo" && (
          <div className="model-select-wrap">
            <select
              className="model-select"
              value={mode}
              onChange={(e) => setMode(e.target.value as ModelMode)}
            >
              {(Object.keys(MODE_INFO) as ModelMode[]).map((m) => (
                <option key={m} value={m}>
                  {MODE_INFO[m].label}
                </option>
              ))}
            </select>
            <span className="model-select-arrow">&#9662;</span>
          </div>
        )}
      </div>

      {tab === "cosmo" ? <ChatPanel mode={mode} /> : <Apollo />}
    </div>
  );
}
