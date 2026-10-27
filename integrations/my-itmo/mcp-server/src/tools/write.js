import { z } from "zod";
import { audit } from "../audit.js";
import { ApiError, assertApiPath } from "../client.js";
import { defineTool } from "../format.js";

const WRITE = { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true };
const DESTRUCTIVE = { ...WRITE, destructiveHint: true };

const confirmField = z
  .boolean()
  .default(false)
  .describe("false (default) = dry run: nothing is sent, the exact request is returned for review. Set true ONLY after the user has explicitly approved this exact action.");

/**
 * Raw writes are limited to these student-facing prefixes. Anything else (staff modules, request-engine administration,
 * payments, e-signing, housing settlement, approvals) is refused no matter what the caller passes.
 */
const WRITE_ALLOW = [
  /^\/api\/requests\/send$/,
  /^\/api\/requests\/my\/\d+$/,
  /^\/api\/queues\/$/,
  /^\/api\/booking\/bookings\/(\d+)?$/,
  /^\/api\/sport\/sign\/(schedule\/(lessons|lesson_groups\/\d+)|competitions\/\d+|projects\/\d+)$/,
  /^\/api\/election\/students\/order(\/(change|clear))?\/?$/,
  /^\/api\/(facultative|intro)\/(booking|commit)\/$/,
];
const WRITE_DENY = /\/pay(\/|$)|agreements|settlement|\/(approve|reject|decline|stop)(\/|$)|\/(gia|constructor|constructor-ep|employments|vacation|dms)\//;

export const isWriteAllowed = (path) => !WRITE_DENY.test(path) && WRITE_ALLOW.some((re) => re.test(path));

/** Run a mutating call: audit it, or return the dry-run preview. */
async function execute({ client, tool, method, path, body, query, confirm, summary }) {
  assertApiPath(path);
  if (!isWriteAllowed(path)) {
    throw new ApiError(`Write to ${path} is not allowed by this MCP (student-facing actions only; payments, e-signing, housing and staff modules are excluded).`);
  }
  const preview = { method, path, ...(query ? { query } : {}), ...(body !== undefined ? { body } : {}) };
  if (!confirm) {
    audit({ tool, ...preview, body: undefined, bodyKeys: bodyKeys(body), dryRun: true });
    return { dry_run: true, would_send: preview, summary, next: "Call again with confirm=true after the user approves." };
  }
  const { status, ok, data } = await client.request(method, path, { query, body });
  audit({ tool, method, path, bodyKeys: bodyKeys(body), dryRun: false, status });
  if (!ok) throw new ApiError(`${method} ${path} → HTTP ${status}: ${typeof data === "string" ? data.slice(0, 300) : JSON.stringify(data).slice(0, 500)}`, { status, body: data });
  return { sent: true, status, summary, response: data };
}

const bodyKeys = (b) => (b && typeof b === "object" ? Object.keys(b) : undefined);

// --- request form → /api/requests/send payload (mirrors the SPA's own serialisation) ---
function formatDate(v) {
  const iso = String(v).match(/^(\d{4})-(\d{2})-(\d{2})/);
  return iso ? `${iso[3]}.${iso[2]}.${iso[1]}` : String(v);
}

export function serialiseField(field, raw) {
  const base = { field_id: String(field.field_id), field_type: field.field_type };
  switch (field.field_type) {
    case "dictionary":
      return { ...base, value: Array.isArray(raw) ? raw.join(",") : String(raw ?? "") };
    case "date":
      return { ...base, value: raw ? formatDate(raw) : "" };
    case "date_time": {
      const m = String(raw).match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}:\d{2})/);
      return { ...base, value: m ? `${m[3]}.${m[2]}.${m[1]} ${m[4]}` : String(raw ?? "") };
    }
    case "multiple_field":
      if (!Array.isArray(raw) || !raw.every(Array.isArray)) throw new ApiError(`Field ${field.field_id} (multiple_field) needs an array of rows, each an array of cell values, e.g. [["a","b"]]`);
      return { ...base, value: JSON.stringify(raw) };
    default:
      return { ...base, value: Array.isArray(raw) ? JSON.stringify(raw) : String(raw ?? "") };
  }
}

export function registerWriteTools(server, { client }) {
  defineTool(
    server,
    "itmo_request_submit",
    {
      title: "Submit a request (заявка)",
      description:
        "Submit a request from the catalog. WRITE: creates a real request in my.itmo.ru. Workflow: itmo_requests scope=catalog → itmo_request_form (fields) → call this WITHOUT confirm to get a validated preview → show it to the user → call again with confirm=true. values maps field_id → value (dictionary: id or array of ids; date: YYYY-MM-DD; date_time: YYYY-MM-DDTHH:mm; multiple_field: array of rows).",
      inputSchema: {
        template_id: z.number().int(),
        values: z.record(z.string(), z.any()).describe('{"19847": "Иванов", "20010": "2026-10-05"}'),
        confirm: confirmField,
      },
      annotations: WRITE,
    },
    async ({ template_id, values, confirm }) => {
      const form = await client.get(`/api/requests/${template_id}`);
      if (form.user_can_apply_now === false) throw new ApiError(`Cannot apply now: ${form.user_cannot_apply_now_reason ?? "not allowed for this account"}`);
      const byId = new Map(form.fields_data.map((f) => [String(f.field_id), f]));
      const unknown = Object.keys(values).filter((id) => !byId.has(id));
      if (unknown.length) throw new ApiError(`Unknown field ids for template ${template_id}: ${unknown.join(", ")}`);
      const missing = form.fields_data.filter((f) => f.required_field_flag && f.show_condition_flag !== false && !f.disabled_field_flag && (values[f.field_id] ?? f.default_value) == null).map((f) => `${f.field_id} (${f.field_name})`);
      if (missing.length) throw new ApiError(`Required fields missing: ${missing.join("; ")}`);
      const merged = { ...Object.fromEntries(form.fields_data.filter((f) => f.default_value != null && !(f.field_id in values)).map((f) => [f.field_id, f.default_value])), ...values };
      const body = { request_id: template_id, values: Object.entries(merged).map(([id, v]) => serialiseField(byId.get(id), v)) };
      return execute({ client, tool: "itmo_request_submit", method: "POST", path: "/api/requests/send", body, confirm, summary: `Submit "${form.template_name}" (template ${template_id}); responsible: ${JSON.stringify(form.responsible_units)}` });
    }
  );

  defineTool(
    server,
    "itmo_request_cancel",
    {
      title: "Withdraw one of my requests",
      description: "Delete (withdraw) a request I submitted. WRITE, destructive. Dry run shows which request would be removed.",
      inputSchema: { request_id: z.number().int(), confirm: confirmField },
      annotations: DESTRUCTIVE,
    },
    async ({ request_id, confirm }) => {
      const req = await client.get(`/api/requests/my/${request_id}`);
      return execute({
        client,
        tool: "itmo_request_cancel",
        method: "DELETE",
        path: `/api/requests/my/${request_id}`,
        confirm,
        summary: `Withdraw request ${request_id} "${req.request_name}" (status: ${req.request_state ?? req.request_status})`,
      });
    }
  );

  defineTool(
    server,
    "itmo_booking_cancel",
    {
      title: "Cancel a room booking",
      description: "Delete one of my room bookings (booking_id from itmo_student_info section=booking_mine). WRITE, destructive.",
      inputSchema: { booking_id: z.number().int(), confirm: confirmField },
      annotations: DESTRUCTIVE,
    },
    ({ booking_id, confirm }) => execute({ client, tool: "itmo_booking_cancel", method: "DELETE", path: `/api/booking/bookings/${booking_id}`, confirm, summary: `Cancel booking ${booking_id}` })
  );

  defineTool(
    server,
    "itmo_sport_unsubscribe",
    {
      title: "Leave a PE section / lesson / competition / project",
      description: "Unsubscribe from a physical-education item. kind: lesson_group (a section) | lesson (single lesson) | competition | project. WRITE, destructive.",
      inputSchema: { kind: z.enum(["lesson_group", "lesson", "competition", "project"]), id: z.number().int(), confirm: confirmField },
      annotations: DESTRUCTIVE,
    },
    ({ kind, id, confirm }) => {
      const target = {
        lesson_group: { path: `/api/sport/sign/schedule/lesson_groups/${id}` },
        lesson: { path: "/api/sport/sign/schedule/lessons", body: [id] },
        competition: { path: `/api/sport/sign/competitions/${id}` },
        project: { path: `/api/sport/sign/projects/${id}` },
      }[kind];
      return execute({ client, tool: "itmo_sport_unsubscribe", method: "DELETE", ...target, confirm, summary: `Unsubscribe from ${kind} ${id}` });
    }
  );

  defineTool(
    server,
    "itmo_api_write",
    {
      title: "Raw write on my.itmo.ru API (restricted)",
      description:
        "Escape hatch for state-changing calls whose payload you know (e.g. from itmo_api_catalog + the front-end). Allowed only for: requests/send, requests/my/{id}, queues, booking/bookings, sport/sign/*, election order, facultative|intro booking/commit. Payments, e-signing, housing settlement, approvals and all staff modules are refused. Dry run by default.",
      inputSchema: {
        method: z.enum(["POST", "PUT", "PATCH", "DELETE"]),
        path: z.string(),
        body: z.any().optional(),
        query: z.record(z.string(), z.union([z.string(), z.number()])).optional(),
        confirm: confirmField,
      },
      annotations: DESTRUCTIVE,
    },
    ({ method, path, body, query, confirm }) => execute({ client, tool: "itmo_api_write", method, path, body, query, confirm, summary: `${method} ${path}` })
  );
}
