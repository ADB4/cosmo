import { useEffect } from "react";

export interface Shortcut {
  keys: string;
  desc: string;
}

/** True when a text field is focused, so global key shortcuts should defer. */
export function isTypingTarget(el: EventTarget | null): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const tag = el.tagName;
  return tag === "TEXTAREA" || tag === "INPUT" || el.isContentEditable;
}

interface Props {
  title?: string;
  shortcuts: Shortcut[];
  onClose: () => void;
}

/** A small modal listing the keyboard shortcuts for the current view. */
export default function ShortcutsOverlay({ title = "Keyboard shortcuts", shortcuts, onClose }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
    };
    // Capture phase so Escape closes the overlay before page-level handlers act.
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [onClose]);

  return (
    <div className="shortcuts-overlay" onClick={onClose}>
      <div className="shortcuts-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-label={title}>
        <div className="shortcuts-header">
          <span className="shortcuts-title">{title}</span>
          <button className="shortcuts-close" onClick={onClose} aria-label="Close">
            &#10005;
          </button>
        </div>
        <ul className="shortcuts-list">
          {shortcuts.map((s, i) => (
            <li key={i} className="shortcuts-row">
              <kbd className="shortcuts-keys">{s.keys}</kbd>
              <span className="shortcuts-desc">{s.desc}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
