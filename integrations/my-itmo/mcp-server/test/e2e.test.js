// Integration test: spawns the real servers over stdio. Needs network + .env credentials; skipped otherwise.
// Never calls a mutating tool with confirm=true.
import assert from "node:assert/strict";
import { test } from "node:test";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { fileURLToPath } from "node:url";
import { loadEnv } from "../src/config.js";

const have = Boolean(loadEnv().MY_ITMO_EMAIL && loadEnv().MY_ITMO_PASSWORD);
const entry = (f) => fileURLToPath(new URL(`../${f}`, import.meta.url));

async function connect(file) {
  const client = new Client({ name: "e2e", version: "0" });
  await client.connect(new StdioClientTransport({ command: process.execPath, args: [entry(file)], stderr: "inherit" }));
  return client;
}
const call = async (c, name, args = {}) => {
  const r = await c.callTool({ name, arguments: args });
  const text = r.content[0].text;
  return { isError: Boolean(r.isError), text, json: r.isError ? null : JSON.parse(text) };
};

test("read-only server exposes no mutating tools", async () => {
  const c = await connect("index.js");
  const { tools } = await c.listTools();
  const names = tools.map((t) => t.name);
  assert.ok(names.includes("itmo_schedule"));
  for (const t of tools) assert.equal(t.annotations?.readOnlyHint, true, `${t.name} must be readOnly`);
  for (const w of ["itmo_request_submit", "itmo_request_cancel", "itmo_api_write", "itmo_booking_cancel", "itmo_sport_unsubscribe"]) assert.ok(!names.includes(w), w);
  await c.close();
});

test("write server adds write tools, all dry-run by default", async () => {
  const c = await connect("write.js");
  const { tools } = await c.listTools();
  const writes = tools.filter((t) => !t.annotations?.readOnlyHint).map((t) => t.name).sort();
  assert.deepEqual(writes, ["itmo_api_write", "itmo_booking_cancel", "itmo_request_cancel", "itmo_request_submit", "itmo_sport_unsubscribe"]);
  for (const t of tools.filter((x) => writes.includes(x.name))) assert.equal(t.inputSchema.properties.confirm.default, false, `${t.name} confirm default`);
  // forbidden targets are refused even with confirm=true (refusal happens before any network call)
  for (const path of ["/api/finances/edupayments/payments/pay", "/api/agreements/agreements/sign-batch", "/api/dormitory/settlement/register", "/api/vacation/me/vacations"]) {
    const r = await call(c, "itmo_api_write", { method: "POST", path, body: {}, confirm: true });
    assert.ok(r.isError && /not allowed/.test(r.text), `${path}: ${r.text}`);
  }
  const dry = await call(c, "itmo_api_write", { method: "DELETE", path: "/api/queues/", body: { x: 1 } });
  assert.equal(dry.json.dry_run, true);
  await c.close();
});

test("public timetable (no login)", async () => {
  const c = await connect("index.js");
  const found = await call(c, "itmo_public_schedule_search", { kind: "teacher", query: "Власова Ассоль" });
  assert.equal(found.json.length, 1);
  const sched = await call(c, "itmo_public_schedule", { kind: "teacher", id: found.json[0].id });
  assert.ok(sched.json.lessons.length > 0);
  assert.ok(sched.json.lessons.every((l) => l.day && l.time && l.subject));
  await c.close();
});

test("sitemap and catalog", async () => {
  const c = await connect("index.js");
  const map = await call(c, "itmo_sitemap", { section: "pages" });
  assert.ok(map.json.pages.length > 50);
  const cat = await call(c, "itmo_api_catalog", { query: "scholarship", audience: "student" });
  assert.ok(cat.json.total >= 3);
  await c.close();
});

test("authenticated reads", { skip: !have && "no credentials in .env" }, async () => {
  const c = await connect("index.js");
  const me = await call(c, "itmo_whoami");
  assert.ok(me.json.isu);
  assert.ok(!/eyJ/.test(me.text), "no token material in output");
  const sched = await call(c, "itmo_schedule");
  assert.ok(Array.isArray(sched.json.days));
  const rb = await call(c, "itmo_record_book");
  assert.ok(Array.isArray(rb.json.plans));
  const reqs = await call(c, "itmo_requests", { scope: "mine" });
  assert.ok(Array.isArray(reqs.json));
  const fin = await call(c, "itmo_finances", { section: "scholarship_total" });
  assert.ok(Array.isArray(fin.json));
  const bad = await call(c, "itmo_api_get", { path: "https://evil.example/api/x" });
  assert.ok(bad.isError);
  await c.close();
});

test("write server dry-runs never send (request_cancel preview)", { skip: !have && "no credentials in .env" }, async () => {
  const c = await connect("write.js");
  const mine = await call(c, "itmo_requests", { scope: "mine" });
  const id = mine.json[0]?.id;
  if (!id) return;
  const dry = await call(c, "itmo_request_cancel", { request_id: id });
  assert.equal(dry.json.dry_run, true);
  assert.equal(dry.json.would_send.method, "DELETE");
  const still = await call(c, "itmo_requests", { scope: "mine" });
  assert.equal(still.json.length, mine.json.length, "nothing was deleted");
  await c.close();
});
