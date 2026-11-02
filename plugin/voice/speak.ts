import { spawn as nodeSpawn } from "node:child_process";

export const DEFAULT_MAX_CHARS = 800;

export type SpawnFn = typeof nodeSpawn;

/**
 * Pull a text part out of a `message.part.updated`-style event.
 * Handles both the V1 shape (`event.properties.part`) and other
 * plausible V2 encodings. Returns undefined for non-text parts.
 */
export function extractPartText(event: unknown): { index: number; text: string } | undefined {
  if (typeof event !== "object" || event === null) return undefined;
  const e = event as Record<string, unknown>;
  const props = (e["properties"] ?? e["payload"] ?? e["data"] ?? e) as Record<string, unknown>;
  const part = (props["part"] ?? e["part"]) as Record<string, unknown> | undefined;
  if (typeof part !== "object" || part === null) return undefined;
  if (part["type"] !== "text") return undefined;
  // Skip user messages when a role is present; we only speak replies.
  const role = part["role"] ?? (props["message"] as Record<string, unknown> | undefined)?.["role"];
  if (role === "user" || role === "human") return undefined;
  const text =
    typeof part["text"] === "string"
      ? part["text"]
      : typeof (part["data"] as Record<string, unknown> | undefined)?.["text"] === "string"
        ? ((part["data"] as Record<string, unknown>)["text"] as string)
        : undefined;
  if (typeof text !== "string" || text.length === 0) return undefined;
  const rawIndex = part["index"];
  const index = typeof rawIndex === "number" ? rawIndex : 0;
  return { index, text };
}

/** Record one streamed text part into the per-turn accumulator. */
export function accumulatePartText(store: Map<number, string>, event: unknown): void {
  const extracted = extractPartText(event);
  if (extracted) store.set(extracted.index, extracted.text);
}

/** Best-effort session ID lookup for `session.idle`-style events. */
export function extractSessionID(event: unknown): string | undefined {
  if (typeof event !== "object" || event === null) return undefined;
  const e = event as Record<string, unknown>;
  for (const key of ["sessionID", "sessionId", "session_id"]) {
    if (typeof e[key] === "string") return e[key] as string;
  }
  for (const container of ["properties", "payload", "data"]) {
    const inner = e[container];
    if (typeof inner === "object" && inner !== null) {
      for (const key of ["sessionID", "sessionId", "session_id"]) {
        const value = (inner as Record<string, unknown>)[key];
        if (typeof value === "string") return value;
      }
    }
  }
  return undefined;
}

/**
 * Fallback: pull assistant text out of a `session.context()`-style
 * result when no streamed parts were accumulated (e.g. the plugin
 * loaded mid-turn). Accepts either an array of `{ info, parts }`
 * entries or `{ messages: [...] }`.
 */
export function extractContextTexts(messages: unknown): string {
  const list = Array.isArray(messages)
    ? messages
    : typeof messages === "object" && messages !== null && Array.isArray((messages as Record<string, unknown>)["messages"])
      ? ((messages as Record<string, unknown>)["messages"] as unknown[])
      : [];
  const texts: string[] = [];
  for (const entry of list) {
    if (typeof entry !== "object" || entry === null) continue;
    const e = entry as Record<string, unknown>;
    const info = (e["info"] ?? e["message"] ?? {}) as Record<string, unknown>;
    const role = info["role"];
    if (role === "user" || role === "human") continue;
    const parts = (e["parts"] ?? []) as unknown[];
    if (!Array.isArray(parts)) continue;
    for (const part of parts) {
      if (typeof part !== "object" || part === null) continue;
      const p = part as Record<string, unknown>;
      if (p["type"] !== "text") continue;
      if (typeof p["text"] === "string" && p["text"].length > 0) texts.push(p["text"] as string);
    }
  }
  // Deterministic order: sort numerically by part index when present.
  return texts.join(" ");
}

/**
 * Join accumulated per-part texts and cap the length (keep the tail,
 * which is usually the conclusion). Returns "" when there is nothing
 * worth speaking.
 */
export function selectSpokenText(store: Map<number, string>, maxChars = DEFAULT_MAX_CHARS): string {
  const ordered = [...store.entries()].sort((a, b) => a[0] - b[0]).map(([, text]) => text);
  const joined = ordered.join(" ");
  if (!joined) return "";
  return joined.length > maxChars ? joined.slice(-maxChars) : joined;
}

/**
 * Pipe text into the TTS wrapper script (default: speak.sh, which
 * forwards to the Kokoro daemon). No shell is involved, so message
 * content cannot inject commands.
 */
export function speakText(tts: string, text: string, spawnFn: SpawnFn = nodeSpawn): Promise<void> {
  return new Promise((resolve) => {
    let child: ReturnType<SpawnFn>;
    try {
      child = spawnFn(tts, [], { stdio: ["pipe", "ignore", "ignore"] });
    } catch {
      resolve();
      return;
    }
    const done = () => resolve();
    child.once("error", done);
    child.once("close", done);
    try {
      if (child.stdin) {
        child.stdin.write(text);
        child.stdin.end();
      } else {
        done();
      }
    } catch {
      done();
    }
  });
}
