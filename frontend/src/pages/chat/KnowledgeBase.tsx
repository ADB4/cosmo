import { useState, useEffect, useCallback, useRef } from "react";
import type { KBStats } from "../../lib/types";
import { fetchStats, ingestFile, ingestDirectory } from "../../lib/api";

interface Props {
  /** Called after any successful ingest so the parent can refresh health. */
  onIngested?: () => void;
  /** Start expanded (e.g. when the KB is empty and needs attention). */
  defaultOpen?: boolean;
}

interface FileResult {
  file: string;
  ok: boolean;
  detail: string;
}

/**
 * Collapsible "Knowledge base" panel for the chat tab: shows indexed doc
 * counts and sources, and lets the user ingest files (PDF / .md / .markdown)
 * or a local directory path into the ChromaDB store.
 */
export default function KnowledgeBase({ onIngested, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen);
  const [stats, setStats] = useState<KBStats | null>(null);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [ingesting, setIngesting] = useState(false);
  const [results, setResults] = useState<FileResult[]>([]);
  const [dirPath, setDirPath] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadStats = useCallback(async () => {
    try {
      setStats(await fetchStats());
      setStatsError(null);
    } catch (e) {
      setStatsError(e instanceof Error ? e.message : "Could not load stats");
    }
  }, []);

  useEffect(() => { loadStats(); }, [loadStats]);

  const ingestFiles = useCallback(
    async (files: File[]) => {
      if (files.length === 0 || ingesting) return;
      setIngesting(true);
      setResults([]);
      for (const file of files) {
        try {
          const res = await ingestFile(file);
          setResults((prev) => [
            ...prev,
            { file: res.filename, ok: true, detail: `${res.chunks_indexed} chunks indexed` },
          ]);
        } catch (e) {
          setResults((prev) => [
            ...prev,
            { file: file.name, ok: false, detail: e instanceof Error ? e.message : String(e) },
          ]);
        }
      }
      setIngesting(false);
      await loadStats();
      onIngested?.();
    },
    [ingesting, loadStats, onIngested],
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files ?? []);
      ingestFiles(files);
      if (fileRef.current) fileRef.current.value = "";
    },
    [ingestFiles],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      ingestFiles(Array.from(e.dataTransfer.files));
    },
    [ingestFiles],
  );

  const handleDirIngest = useCallback(async () => {
    const path = dirPath.trim();
    if (!path || ingesting) return;
    setIngesting(true);
    setResults([]);
    try {
      const res = await ingestDirectory(path);
      setResults(
        res.files.map((f) => ({
          file: f.file,
          ok: f.error == null,
          detail: f.error ?? `${f.chunks ?? 0} chunks indexed`,
        })),
      );
    } catch (e) {
      setResults([{ file: path, ok: false, detail: e instanceof Error ? e.message : String(e) }]);
    } finally {
      setIngesting(false);
      await loadStats();
      onIngested?.();
    }
  }, [dirPath, ingesting, loadStats, onIngested]);

  const sourceEntries = stats ? Object.entries(stats.sources) : [];

  return (
    <div className={`kb-panel ${open ? "kb-panel--open" : ""}`}>
      <button className="kb-header" onClick={() => setOpen((o) => !o)}>
        <span className="kb-caret">{open ? "▾" : "▸"}</span>
        <span className="kb-title">Knowledge base</span>
        <span className="kb-summary">
          {stats
            ? `${stats.total_documents} document${stats.total_documents !== 1 ? "s" : ""} · ${stats.total_chunks} chunks`
            : statsError
              ? "unavailable"
              : "…"}
        </span>
      </button>

      {open && (
        <div className="kb-body">
          {statsError && <div className="kb-error">{statsError}</div>}

          {sourceEntries.length > 0 ? (
            <ul className="kb-sources">
              {sourceEntries
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([src, info]) => (
                  <li key={src} className="kb-source">
                    <span className="kb-source-name">{src}</span>
                    <span className="kb-source-meta">{info.type} · {info.chunks} chunks</span>
                  </li>
                ))}
            </ul>
          ) : (
            <div className="kb-empty">No documents indexed yet. Add some below.</div>
          )}

          <div
            className={`kb-drop ${dragOver ? "kb-drop--over" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
          >
            {ingesting ? "Ingesting…" : "Drop PDF / .md / .markdown here, or click to choose"}
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.md,.markdown"
              multiple
              hidden
              onChange={handleFileInput}
              disabled={ingesting}
            />
          </div>

          <div className="kb-dir-row">
            <input
              className="kb-dir-input"
              type="text"
              value={dirPath}
              placeholder="Or ingest a directory path, e.g. /path/to/docs"
              onChange={(e) => setDirPath(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleDirIngest(); }}
              disabled={ingesting}
            />
            <button
              className="kb-dir-btn"
              onClick={handleDirIngest}
              disabled={!dirPath.trim() || ingesting}
            >
              Ingest
            </button>
          </div>

          {results.length > 0 && (
            <ul className="kb-results">
              {results.map((r, i) => (
                <li key={i} className={`kb-result ${r.ok ? "kb-result--ok" : "kb-result--err"}`}>
                  <span className="kb-result-file">{r.file}</span>
                  <span className="kb-result-detail">{r.detail}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
