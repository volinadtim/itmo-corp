#!/usr/bin/env node
/**
 * Rebuilds data/sitemap.json and data/api-catalog.json from the live my.itmo.ru front-end bundle.
 *
 *   node scripts/crawl-sitemap.mjs            # static analysis of the public JS bundle (no login)
 *   node scripts/crawl-sitemap.mjs --probe    # also log in and GET every parameter-free student endpoint (read-only)
 *
 * The bundle is public; --probe only issues GET requests and records HTTP status + response shape (never values).
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { PROJECT_ROOT, SERVER_ROOT } from "../src/config.js";

const ORIGIN = "https://my.itmo.ru";
const DATA_DIR = join(SERVER_ROOT, "data");
const probe = process.argv.includes("--probe");

const getText = async (path) => {
  for (let attempt = 1; ; attempt++) {
    try {
      const res = await fetch(ORIGIN + path, { signal: AbortSignal.timeout(60_000) });
      if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
      return await res.text();
    } catch (err) {
      if (attempt >= 3) throw err;
      await new Promise((r) => setTimeout(r, 1000 * attempt));
    }
  }
};

// ---------- 1. download every JS chunk ----------
const loginHtml = await getText("/login");
const entry = [...loginHtml.matchAll(/<script[^>]+src="(\/_nuxt\/[^"]+\.js)"/g)].map((m) => m[1]);
const sources = {};
for (const p of entry) sources[p] = await getText(p);
const runtime = Object.values(sources).find((s) => s.includes("webpackJsonp") && /return\s*\w\.p\+""\+\{/.test(s));
if (!runtime) throw new Error("webpack runtime not found — front-end build changed");
const chunkMap = runtime.match(/return\s*\w\.p\+""\+(\{[^}]+\})\[\w\]/)[1];
const chunkHashes = [...chunkMap.matchAll(/\d+:"([0-9a-f]+)"/g)].map((m) => m[1]);
await Promise.all(
  chunkHashes.map(async (h) => {
    sources[`/_nuxt/${h}.js`] = await getText(`/_nuxt/${h}.js`).catch(() => "");
  })
);
console.error(`downloaded ${Object.keys(sources).length} bundles`);

// ---------- 2. routes ----------
const routes = new Map();
for (const src of Object.values(sources)) {
  for (const m of src.matchAll(/\{path:"(\/[^"]*)",component:function\(\)\{return[^]{0,500}?\},name:"([^"]+)"/g)) routes.set(m[1], m[2]);
}

// ---------- 3. API endpoints ----------
const isIdent = (c) => /[\w$]/.test(c);

/** Index of the first top-level `,` or `)` at/after i (strings and brackets respected). */
function endOfExpr(src, i) {
  let depth = 0;
  for (; i < src.length; i++) {
    const c = src[i];
    if (c === '"' || c === "'" || c === "`") {
      for (i++; i < src.length && src[i] !== c; i++) if (src[i] === "\\") i++;
    } else if ("([{".includes(c)) depth++;
    else if (")]}".includes(c)) {
      if (depth === 0) return i;
      depth--;
    } else if (c === "," && depth === 0) return i;
  }
  return i;
}

function splitTopLevel(s, sep) {
  const parts = [];
  let start = 0;
  let depth = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '"' || c === "'" || c === "`") {
      for (i++; i < s.length && s[i] !== c; i++) if (s[i] === "\\") i++;
    } else if ("([{".includes(c)) depth++;
    else if (")]}".includes(c)) depth--;
    else if (c === sep && depth === 0) {
      parts.push(s.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(s.slice(start));
  return parts;
}

const strLit = (s) => (/^(["'])(.*)\1$/s.test(s.trim()) ? s.trim().slice(1, -1) : null);
function paramName(expr) {
  const m = expr.replace(/\.toString\(\)|\(\)/g, "").match(/([A-Za-z_$][\w$]*)\s*\)*$/);
  return m && m[1].length > 2 ? m[1] : "id";
}
const piece = (arg) => strLit(arg) ?? `{${paramName(arg)}}`;

function exprToPath(expr) {
  expr = expr.trim();
  if (expr.startsWith("`")) return expr.slice(1, -1).replace(/\$\{([^}]*)\}/g, (_, e) => `{${paramName(e)}}`);
  let out = "";
  for (const part of splitTopLevel(expr, "+")) {
    const p = part.trim();
    const lit = p.match(/^(["'])((?:\\.|(?!\1).)*)\1/s);
    if (lit) {
      out += lit[2];
      let rest = p.slice(lit[0].length);
      while (rest.startsWith(".concat(")) {
        let depth = 0;
        let i = ".concat".length;
        for (; i < rest.length; i++) {
          if (rest[i] === "(") depth++;
          else if (rest[i] === ")" && --depth === 0) break;
        }
        for (const a of splitTopLevel(rest.slice(".concat(".length, i), ",")) out += piece(a);
        rest = rest.slice(i + 1);
      }
    } else out += `{${paramName(p)}}`;
  }
  return out;
}

const endpoints = new Map(); // "METHOD path" → {method, path, query:Set}
for (const src of Object.values(sources)) {
  for (const m of src.matchAll(/\.(get|post|put|patch|delete)\(\s*(?=["'`])/g)) {
    const start = m.index + m[0].length;
    const end = endOfExpr(src, start);
    const path = exprToPath(src.slice(start, end)).trim();
    if (!path.startsWith("/api/")) continue;
    const method = m[1].toUpperCase();
    const key = `${method} ${path}`;
    const entry = endpoints.get(key) ?? { method, path, query: new Set() };
    const opts = src.slice(end, end + 400);
    const params = opts.match(/^,\s*\{\s*params:\s*\{([^}]*)\}/);
    if (params) for (const k of params[1].matchAll(/(?:^|,)\s*([A-Za-z_]\w*)\s*:/g)) entry.query.add(k[1]);
    endpoints.set(key, entry);
  }
}

// ---------- 4. classification ----------
const STAFF_MODULES = ["constructor", "constructor-ep", "gia", "employments", "vacation"];
const MIXED_V2 = /^\/api\/requests\/v2\/(admin|access-definitions|processes|forms|platform-roles|dictionaries\/admin|categories|context-enrichments|prefills|users|tasks)/;
const RISK = [
  [/\/pay(\/|$)|\/payments\/pay/, "financial"],
  [/\/agreements\/.*sign/, "legal"],
  [/\/settlement\//, "housing"],
  [/\/(approve|reject|decline|stop)(\/|$)/, "approval"],
];
function classify({ method, path }) {
  const seg = path.split("/");
  const module = seg[2];
  let audience = "student";
  if (STAFF_MODULES.includes(module)) audience = "staff";
  else if (module === "services" && seg[3] === "adviser") audience = "adviser";
  else if (path.startsWith("/api/requests/v2/")) audience = MIXED_V2.test(path) ? "staff" : "mixed";
  const risk = RISK.find(([re]) => re.test(path))?.[1] ?? null;
  return { module, audience, mutating: method !== "GET", risk };
}

const catalog = [...endpoints.values()]
  .map((e) => ({ method: e.method, path: e.path, ...(e.query.size ? { query: [...e.query] } : {}), ...classify(e) }))
  .sort((a, b) => a.path.localeCompare(b.path) || a.method.localeCompare(b.method));

// ---------- 5. optional live probe (GET only) ----------
let menu = null;
if (probe) {
  const { ItmoSession } = await import("../src/auth.js");
  const { ItmoClient } = await import("../src/client.js");
  const client = new ItmoClient(new ItmoSession());
  const shape = (v, d = 0) => {
    if (Array.isArray(v)) return v.length ? [shape(v[0], d + 1)] : [];
    if (v && typeof v === "object") return d >= 2 ? "object" : Object.fromEntries(Object.entries(v).slice(0, 25).map(([k, x]) => [k, shape(x, d + 1)]));
    return v === null ? "null" : typeof v;
  };
  const SKIP = /bypass|\/download|\/pay/;
  for (const e of catalog) {
    if (e.method !== "GET" || e.audience === "staff" || e.audience === "adviser" || /[{]/.test(e.path) || e.query?.length || SKIP.test(e.path)) continue;
    const r = await client.request("GET", e.path, { timeoutMs: 20_000 }).catch((err) => ({ status: 0, data: String(err.message) }));
    e.probe = { status: r.status, ...(r.status === 200 && typeof r.data === "object" ? { shape: shape(r.data.result ?? r.data.data ?? r.data) } : {}) };
    console.error(r.status, e.path);
    await new Promise((res) => setTimeout(res, 120));
  }
  const m1 = await client.get("/api/system/v1/menu/items");
  const m2 = await client.get("/api/system/v1/menu/services");
  menu = { items: m1.menu, services: m2.menu };
}

// ---------- 6. write ----------
const publicSites = [
  { host: "my.itmo.ru", purpose: "Student personal cabinet (Nuxt SPA + /api JSON, ITMO ID Bearer auth)" },
  { host: "id.itmo.ru", purpose: "ITMO ID — Keycloak realm 'itmo' (OIDC provider)" },
  { host: "itmo.ru/ru/schedule", purpose: "Public timetable by teacher / group / room (server-rendered HTML, no login)" },
  { host: "isu.ifmo.ru", purpose: "Legacy ISU portal (not covered by the MCP)" },
  { host: "abit.itmo.ru", purpose: "Admissions portal (not covered by the MCP)" },
  { host: "helpdesk.itmo.ru", purpose: "Support desk (Jira Service Management)" },
];
mkdirSync(DATA_DIR, { recursive: true });
writeFileSync(
  join(DATA_DIR, "sitemap.json"),
  JSON.stringify({ generatedAt: new Date().toISOString(), origin: ORIGIN, publicSites, routes: [...routes].map(([path, name]) => ({ path, name })).sort((a, b) => a.path.localeCompare(b.path)), ...(menu ? { menu } : {}) }, null, 1)
);
// keep previously probed results when run without --probe
if (!probe) {
  try {
    const old = new Map(JSON.parse(readFileSync(join(DATA_DIR, "api-catalog.json"), "utf8")).endpoints.map((e) => [`${e.method} ${e.path}`, e.probe]));
    for (const e of catalog) if (old.get(`${e.method} ${e.path}`)) e.probe = old.get(`${e.method} ${e.path}`);
  } catch {
    /* first run */
  }
}
writeFileSync(join(DATA_DIR, "api-catalog.json"), JSON.stringify({ generatedAt: new Date().toISOString(), endpoints: catalog }, null, 1));
console.error(`routes: ${routes.size}, endpoints: ${catalog.length}${probe ? " (probed)" : ""}`);

// ---------- 7. human-readable map ----------
const sm = JSON.parse(readFileSync(join(DATA_DIR, "sitemap.json"), "utf8"));
const MODULE_TOOLS = {
  schedule: "itmo_schedule",
  record_book: "itmo_record_book",
  requests: "itmo_requests, itmo_request_*",
  finances: "itmo_finances",
  dormitory: "itmo_student_info (dormitory_*)",
  sport: "itmo_student_info (sport_*), itmo_sport_calendar",
  practices: "itmo_student_info (practices_programs)",
  election: "itmo_student_info (election_*)",
  facultative: "itmo_student_info (facultative_status)",
  intro: "itmo_student_info (intro_status)",
  queues: "itmo_student_info (queues_*)",
  booking: "itmo_student_info (booking_*)",
  agreements: "itmo_student_info (agreements) — read only",
  "individual-plan": "itmo_student_info (individual_plan_*)",
  personalities: "itmo_people_search",
  system: "itmo_student_info (dashboard), itmo_sitemap",
  "gia-students": "itmo_student_info (diplomas_mine)",
};
const lines = [
  "# Карта my.itmo.ru",
  "",
  `Сгенерировано \`scripts/crawl-sitemap.mjs\` ${new Date().toISOString().slice(0, 10)}${probe ? " (с живой проверкой GET под учёткой студента)" : ""}. Источник — публичный фронтенд-бандл и API портала; обновить: \`npm run crawl:probe\` в \`integrations/my-itmo/mcp-server\`.`,
  "",
  "## Сайты",
  "",
  ...sm.publicSites.map((s) => `- **${s.host}** — ${s.purpose}`),
  "",
  "## Страницы (SPA-маршруты)",
  "",
  "| Путь | Имя |",
  "|---|---|",
  ...sm.routes.map((r) => `| \`${r.path}\` | ${r.name} |`),
  "",
];
if (sm.menu) {
  lines.push("## Меню (для текущей учётки)", "");
  const walk = (items, d = 0) => {
    for (const i of items ?? []) {
      lines.push(`${"  ".repeat(d)}- \`${i.to}\` — ${i.description || i.title}`);
      walk(i.children ?? i.items, d + 1);
    }
  };
  walk(sm.menu.items);
  lines.push("", "### Сервисы", "");
  walk(sm.menu.services);
  lines.push("");
}
lines.push("## API по модулям", "", "`/api/<module>/…`, авторизация `Authorization: Bearer <ITMO ID access token>`. Аудитория: **student** — доступно студенту; **mixed** — зависит от роли; **adviser/staff** — сотрудники (MCP их не использует). Статус — результат последней живой проверки GET (200 работает, 403 закрыто для этой учётки сейчас).", "");
const byModule = Map.groupBy(catalog, (e) => e.module);
for (const [module, eps] of [...byModule].sort(([a], [b]) => a.localeCompare(b))) {
  const aud = [...new Set(eps.map((e) => e.audience))].join("/");
  lines.push(`### ${module} (${aud}, ${eps.length})`, "");
  if (MODULE_TOOLS[module]) lines.push(`MCP: ${MODULE_TOOLS[module]}`, "");
  if (aud === "staff") {
    lines.push("Служебный модуль, эндпоинты см. в `data/api-catalog.json`.", "");
    continue;
  }
  lines.push("| | Путь | Query | Риск | Статус |", "|---|---|---|---|---|");
  for (const e of eps) lines.push(`| ${e.method} | \`${e.path}\` | ${e.query?.join(", ") ?? ""} | ${e.risk ?? ""} | ${e.probe?.status ?? ""} |`);
  lines.push("");
}
writeFileSync(join(PROJECT_ROOT, "integrations/my-itmo/references/sitemap.md"), lines.join("\n"));
