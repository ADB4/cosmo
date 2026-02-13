import { useState, useRef } from "react";
import type { ModelMode, HealthResponse, KBStats } from "./types";
import { MODE_INFO } from "./types";
import { fetchStats, ingestFile } from "./api";

interface SidebarProps {
  mode: ModelMode;
  onModeChange: (m: ModelMode) => void;
  health: HealthResponse | null;
  onRefreshHealth: () => void;
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({
  mode,
  onModeChange,
  health,
  onRefreshHealth,
  open,
  onClose,
}: SidebarProps) {
  const [stats, setStats] = useState<KBStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadStats = async () => {
    setStatsLoading(true);
    try {
      setStats(await fetchStats());
    } catch (e) {
      setStats(null);
    } finally {
      setStatsLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus(null);
    try {
      const result = await ingestFile(file);
      setUploadStatus(
        result.chunks_indexed > 0
          ? `Indexed ${result.chunks_indexed} chunks from ${result.filename}`
          : `${result.filename} already indexed`,
      );
      onRefreshHealth();
    } catch (err: unknown) {
      setUploadStatus(
        `Error: ${err instanceof Error ? err.message : String(err)}`,
      );
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const modes: ModelMode[] = ["quick", "deep", "general", "fast"];

  return (
    <aside className={`sidebar ${open ? "sidebar--open" : ""}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <span className="brand-dot" />
        <span className="brand-name">cosmo</span>
        <span className="brand-sub">study companion</span>
      </div>

      {/* Status */}
      <div className="sidebar-section">
        <div className="section-label">Status</div>
        <div className={`status-badge status-badge--${health?.status ?? "unknown"}`}>
          <span className="status-dot" />
          {health?.status === "ok"
            ? `${health.total_documents ?? 0} docs / ${health.total_chunks ?? 0} chunks`
            : health?.message ?? "checking..."}
        </div>
      </div>

      {/* Mode selector */}
      <div className="sidebar-section">
        <div className="section-label">Model</div>
        <div className="mode-list">
          {modes.map((m) => (
            <button
              key={m}
              className={`mode-btn ${m === mode ? "mode-btn--active" : ""}`}
              onClick={() => {
                onModeChange(m);
                onClose();
              }}
            >
              <span className="mode-btn-label">{MODE_INFO[m].label}</span>
              <span className="mode-btn-desc">{MODE_INFO[m].description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Upload */}
      <div className="sidebar-section">
        <div className="section-label">Add Documents</div>
        <label className={`upload-btn ${uploading ? "upload-btn--busy" : ""}`}>
          {uploading ? "Processing..." : "Upload PDF / Markdown"}
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.md,.markdown"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.startsWith("Error") ? "upload-status--error" : ""}`}>
            {uploadStatus}
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="sidebar-section">
        <button className="stats-btn" onClick={loadStats} disabled={statsLoading}>
          {statsLoading ? "Loading..." : "View Knowledge Base"}
        </button>
        {stats && (
          <div className="stats-detail">
            <div className="stats-row">
              <span>{stats.total_documents} documents</span>
              <span>{stats.total_chunks} chunks</span>
            </div>
            <ul className="stats-sources">
              {Object.entries(stats.sources)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([name, info]) => (
                  <li key={name}>
                    <span className="source-name">{name}</span>
                    <span className="source-meta">
                      {info.type} &middot; {info.chunks}
                    </span>
                  </li>
                ))}
            </ul>
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <span>Local LLMs via Ollama</span>
      </div>
    </aside>
  );
}
