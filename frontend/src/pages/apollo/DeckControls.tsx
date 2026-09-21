import { useState, useRef, useCallback } from "react";
import { createModule, ingestQuiz } from "../../lib/api";

interface Props {
  /** Module names that already exist (disk + derived). */
  existingModules: string[];
  /** Called after a module is created or a deck is uploaded, to refresh. */
  onChanged: () => void;
  /** Pre-select this module in the uploader (e.g. the open module). */
  initialModule?: string;
}

const NEW_MODULE = "\x00__new__";

/**
 * Deck-management controls: create an empty module, and upload a deck JSON
 * into an existing or brand-new module. Used on the module picker and the
 * empty state so a first-time user always has a path to load a deck.
 */
export default function DeckControls({ existingModules, onChanged, initialModule }: Props) {
  const [newModule, setNewModule] = useState("");
  const [creating, setCreating] = useState(false);
  const [createMsg, setCreateMsg] = useState<string | null>(null);

  // Upload target: an existing module name, or NEW_MODULE + a typed name
  const [target, setTarget] = useState<string>(initialModule ?? existingModules[0] ?? NEW_MODULE);
  const [targetNew, setTargetNew] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleCreate = useCallback(async () => {
    const name = newModule.trim();
    if (!name || creating) return;
    setCreating(true);
    setCreateMsg(null);
    try {
      const res = await createModule(name);
      setCreateMsg(`Created module "${res.module}"`);
      setNewModule("");
      onChanged();
    } catch (e) {
      setCreateMsg(`Error: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setCreating(false);
    }
  }, [newModule, creating, onChanged]);

  const handleFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const mod = (target === NEW_MODULE ? targetNew : target).trim();
      if (!mod) {
        setUploadMsg("Error: choose or name a target module first");
        if (fileRef.current) fileRef.current.value = "";
        return;
      }
      setUploading(true);
      setUploadMsg(null);
      try {
        const result = await ingestQuiz(file, mod);
        setUploadMsg(
          `Loaded ${result.total_questions} questions from ${result.filename} into "${result.module}"`,
        );
        onChanged();
      } catch (err) {
        setUploadMsg(`Error: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setUploading(false);
        if (fileRef.current) fileRef.current.value = "";
      }
    },
    [target, targetNew, onChanged],
  );

  return (
    <div className="deck-controls">
      <div className="deck-controls-row">
        <span className="deck-controls-label">New module</span>
        <input
          className="deck-controls-input"
          type="text"
          value={newModule}
          placeholder="e.g. algorithms"
          onChange={(e) => setNewModule(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleCreate();
          }}
        />
        <button
          className="deck-controls-btn"
          onClick={handleCreate}
          disabled={!newModule.trim() || creating}
        >
          {creating ? "Creating…" : "Create"}
        </button>
      </div>
      {createMsg && (
        <span className={`deck-controls-msg ${createMsg.startsWith("Error") ? "deck-controls-msg--error" : ""}`}>
          {createMsg}
        </span>
      )}

      <div className="deck-controls-row">
        <span className="deck-controls-label">Upload deck</span>
        <select
          className="deck-controls-select"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
        >
          {existingModules.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
          <option value={NEW_MODULE}>New module…</option>
        </select>
        {target === NEW_MODULE && (
          <input
            className="deck-controls-input"
            type="text"
            value={targetNew}
            placeholder="module name"
            onChange={(e) => setTargetNew(e.target.value)}
          />
        )}
        <label className={`deck-controls-btn ${uploading ? "deck-controls-btn--busy" : ""}`}>
          {uploading ? "Processing…" : "Choose JSON"}
          <input
            ref={fileRef}
            type="file"
            accept=".json"
            onChange={handleFile}
            disabled={uploading}
            hidden
          />
        </label>
      </div>
      {uploadMsg && (
        <span className={`deck-controls-msg ${uploadMsg.startsWith("Error") ? "deck-controls-msg--error" : ""}`}>
          {uploadMsg}
        </span>
      )}
    </div>
  );
}
