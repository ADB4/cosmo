import { useState, useEffect, useCallback, useMemo } from "react";
import ChatPanel from "./pages/chat/ChatPanel";
import Apollo from "./pages/apollo/Apollo";
import { fetchHealth, fetchInstalledModes } from "./lib/api";
import type { ModelMode, HealthResponse } from "./lib/types";
import { MODE_INFO } from "./lib/types";

type Tab = "cosmo" | "apollo";

export default function App() {
  const [tab, setTab] = useState<Tab>("cosmo");
  const [mode, setMode] = useState<ModelMode>("qwen3-coder-30b");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  // Installed modes (from /api/models); empty until loaded or if unavailable.
  const [installedModes, setInstalledModes] = useState<string[]>([]);

  const checkHealth = useCallback(async () => {
    try {
      setHealth(await fetchHealth());
    } catch {
      setHealth({ status: "error", message: "Cannot reach backend" });
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const id = setInterval(checkHealth, 10000);
    return () => clearInterval(id);
  }, [checkHealth]);

  // Load which configured models are actually installed, to collapse the
  // dropdown. Refetch when health flips to ok (e.g. Ollama came back).
  useEffect(() => {
    if (health?.status === "ok") {
      fetchInstalledModes().then(setInstalledModes);
    }
  }, [health?.status]);

  // Modes to offer: installed ∩ curated (MODE_INFO). Fall back to all
  // curated modes when the models endpoint hasn't answered / is empty.
  const availableModes = useMemo(() => {
    const curated = Object.keys(MODE_INFO) as ModelMode[];
    const installedCurated = curated.filter((m) => installedModes.includes(m));
    return installedCurated.length > 0 ? installedCurated : curated;
  }, [installedModes]);

  // If the selected mode isn't available, switch to the first that is.
  useEffect(() => {
    if (!availableModes.includes(mode) && availableModes.length > 0) {
      setMode(availableModes[0]!);
    }
  }, [availableModes, mode]);

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
              {availableModes.map((m) => (
                <option key={m} value={m}>
                  {MODE_INFO[m].label}
                </option>
              ))}
            </select>
            <span className="model-select-arrow">&#9662;</span>
          </div>
        )}
      </div>

      {tab === "cosmo" ? (
        <ChatPanel mode={mode} health={health} onHealthRefresh={checkHealth} />
      ) : (
        <Apollo mode={mode} />
      )}
    </div>
  );
}
