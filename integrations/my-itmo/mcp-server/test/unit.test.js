import assert from "node:assert/strict";
import { test } from "node:test";
import { ApiError, assertApiPath, unwrap } from "../src/client.js";
import { currentWeek } from "../src/format.js";
import { isWriteAllowed, serialiseField } from "../src/tools/write.js";

test("assertApiPath accepts same-origin /api paths only", () => {
  assert.doesNotThrow(() => assertApiPath("/api/schedule/meta/time_slots"));
  assert.doesNotThrow(() => assertApiPath("/api/record_book/1/2?x=1"));
  for (const bad of ["https://evil.example/api/x", "//evil.example/api/x", "/api/../etc", "/apix/y", "api/x", "/api/a b", "/api/a\\b", ""]) {
    assert.throws(() => assertApiPath(bad), ApiError, bad);
  }
});

test("unwrap handles both response envelopes", () => {
  assert.deepEqual(unwrap({ error_code: 0, error_message: null, result: [1] }), [1]);
  assert.deepEqual(unwrap({ error_code: null, result: { a: 1 } }), { a: 1 });
  assert.deepEqual(unwrap({ code: 0, data: [2], message: null }), [2]);
  assert.throws(() => unwrap({ error_code: 3, error_message: "nope", result: null }), /nope/);
  assert.throws(() => unwrap({ code: 1, data: null, message: "bad" }), /bad/);
  assert.equal(unwrap("plain"), "plain");
});

test("raw write allowlist: student actions yes; money, e-signing, housing, staff no", () => {
  for (const ok of ["/api/requests/send", "/api/requests/my/1119150", "/api/queues/", "/api/booking/bookings/", "/api/booking/bookings/42", "/api/sport/sign/schedule/lessons", "/api/sport/sign/schedule/lesson_groups/7", "/api/sport/sign/competitions/3", "/api/election/students/order/change"]) {
    assert.ok(isWriteAllowed(ok), ok);
  }
  for (const no of [
    "/api/finances/edupayments/payments/pay",
    "/api/dormitory/payments/pay",
    "/api/agreements/agreements/sign-batch",
    "/api/agreements/agreements/5/sign",
    "/api/dormitory/settlement/register",
    "/api/gia/experts/approve/1",
    "/api/vacation/me/vacations",
    "/api/employments/employments/1/approve",
    "/api/constructor/programs/1",
    "/api/requests/v2/admin/process-instances",
    "/api/requests/v2/processes/deploy",
    "/api/requests/my/abc",
    "/api/individual-plan/plan",
  ]) {
    assert.equal(isWriteAllowed(no), false, no);
  }
});

test("request field serialisation mirrors the SPA", () => {
  assert.deepEqual(serialiseField({ field_id: 1, field_type: "text" }, "Иванов"), { field_id: "1", field_type: "text", value: "Иванов" });
  assert.equal(serialiseField({ field_id: 2, field_type: "date" }, "2026-10-05").value, "05.10.2026");
  assert.equal(serialiseField({ field_id: 3, field_type: "date_time" }, "2026-10-05T14:30").value, "05.10.2026 14:30");
  assert.equal(serialiseField({ field_id: 4, field_type: "dictionary" }, [1, 2]).value, "1,2");
  assert.equal(serialiseField({ field_id: 5, field_type: "multiple_field" }, [["a", "b"]]).value, '[["a","b"]]');
});

test("currentWeek spans Monday to Sunday", () => {
  const { start, end } = currentWeek();
  assert.equal(new Date(start).getUTCDay(), 1);
  assert.equal((new Date(end) - new Date(start)) / 86_400_000, 6);
});
