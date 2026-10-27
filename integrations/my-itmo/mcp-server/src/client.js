import { BASE_URL } from "./config.js";

export class ApiError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

/**
 * Only same-origin /api/ paths are allowed, so a tool argument can never redirect the Bearer token to another host.
 */
export function assertApiPath(path) {
  if (typeof path !== "string" || !path.startsWith("/api/") || /\/\/|\\|\.\.|[\s\0]/.test(path.split("?")[0])) {
    throw new ApiError(`Invalid API path: ${JSON.stringify(path)} (must start with /api/ and contain no "..", "//" or whitespace)`);
  }
}

/**
 * The portal answers in two envelopes: {error_code, error_message, result} and {code, data, message}.
 * Returns the payload or throws with the server's message.
 */
export function unwrap(body) {
  if (body && typeof body === "object" && !Array.isArray(body)) {
    if ("error_code" in body) {
      if (body.error_code) throw new ApiError(String(body.error_message ?? `error_code ${body.error_code}`), { body });
      return body.result;
    }
    if ("code" in body && "data" in body) {
      if (body.code) throw new ApiError(String(body.message ?? `code ${body.code}`), { body });
      return body.data;
    }
  }
  return body;
}

export class ItmoClient {
  constructor(session) {
    this.session = session;
  }

  /** @returns {Promise<{status:number, ok:boolean, data:any}>} */
  async request(method, path, { query, body, headers, timeoutMs = 30_000 } = {}) {
    assertApiPath(path);
    const url = new URL(BASE_URL + path);
    for (const [k, v] of Object.entries(query ?? {})) {
      if (v === undefined || v === null) continue;
      for (const item of Array.isArray(v) ? v : [v]) url.searchParams.append(k, String(item));
    }
    const idempotent = method === "GET";
    let refreshed = false;
    for (let attempt = 0; ; attempt++) {
      let res;
      try {
        res = await fetch(url, {
          method,
          signal: AbortSignal.timeout(timeoutMs),
          headers: {
            authorization: `Bearer ${await this.session.accessToken({ force: refreshed })}`,
            accept: "application/json",
            ...(body !== undefined ? { "content-type": "application/json" } : {}),
            ...headers,
          },
          body: body !== undefined ? JSON.stringify(body) : undefined,
        });
      } catch (err) {
        if (idempotent && attempt < 2) {
          await sleep(500 * 2 ** attempt);
          continue;
        }
        throw new ApiError(`Network error calling ${method} ${path}: ${err.message}`);
      }
      if (res.status === 401 && !refreshed) {
        refreshed = true;
        continue;
      }
      if (idempotent && [502, 503, 504].includes(res.status) && attempt < 2) {
        await sleep(500 * 2 ** attempt);
        continue;
      }
      const text = await res.text();
      let data = text;
      try {
        data = text ? JSON.parse(text) : null;
      } catch {
        /* plain-text error pages (404 page not found, nil-pointer panics) stay as text */
      }
      return { status: res.status, ok: res.ok, data };
    }
  }

  /** GET + envelope unwrap; throws ApiError on HTTP or application errors. */
  async get(path, query) {
    return this.#call("GET", path, { query });
  }

  async send(method, path, body, query) {
    return this.#call(method, path, { body, query });
  }

  async #call(method, path, opts) {
    const { status, ok, data } = await this.request(method, path, opts);
    if (!ok) {
      const msg = typeof data === "string" ? data.slice(0, 300) : (data?.error_message ?? data?.message ?? JSON.stringify(data)?.slice(0, 300));
      throw new ApiError(`${method} ${path} → HTTP ${status}: ${msg}`, { status, body: data });
    }
    return unwrap(data);
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
