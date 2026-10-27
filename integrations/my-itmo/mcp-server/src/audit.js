import { appendFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { SESSION_DIR } from "./config.js";

/** Append-only JSONL log of every mutating call (bodies are never logged, only their keys). */
export function audit(entry) {
  try {
    mkdirSync(SESSION_DIR, { recursive: true, mode: 0o700 });
    appendFileSync(join(SESSION_DIR, "audit.log"), JSON.stringify({ ts: new Date().toISOString(), ...entry }) + "\n", { mode: 0o600 });
  } catch {
    /* auditing must never break a tool call */
  }
}
