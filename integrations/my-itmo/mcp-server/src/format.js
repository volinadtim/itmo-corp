import { MAX_CHARS } from "./config.js";

function clip(text) {
  if (text.length <= MAX_CHARS) return text;
  return `${text.slice(0, MAX_CHARS)}\n…[truncated: ${text.length - MAX_CHARS} more characters. Narrow the request (dates, ids, section) or raise ITMO_MCP_MAX_CHARS]`;
}

export const ok = (value) => ({
  content: [{ type: "text", text: clip(typeof value === "string" ? value : JSON.stringify(value)) }],
});

export const fail = (err) => ({
  isError: true,
  content: [{ type: "text", text: `Error: ${err instanceof Error ? err.message : String(err)}` }],
});

/** registerTool wrapper: uniform error handling, so handlers just return data or throw. */
export function defineTool(server, name, config, handler) {
  server.registerTool(name, config, async (args, extra) => {
    try {
      return ok(await handler(args ?? {}, extra));
    } catch (err) {
      return fail(err);
    }
  });
}

/** Today's date parts in Moscow time (the portal's timezone). */
export function moscowToday() {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Moscow", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  return parts; // YYYY-MM-DD
}

export function currentWeek() {
  const today = new Date(`${moscowToday()}T00:00:00Z`);
  const dow = (today.getUTCDay() + 6) % 7; // Monday = 0
  const iso = (d) => d.toISOString().slice(0, 10);
  const start = new Date(today.getTime() - dow * 86_400_000);
  return { start: iso(start), end: iso(new Date(start.getTime() + 6 * 86_400_000)) };
}
