import { createHash, randomBytes } from "node:crypto";
import { chmodSync, existsSync, mkdirSync, readFileSync, renameSync, unlinkSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { OIDC, SESSION_DIR, loadEnv } from "./config.js";

const TOKEN_FILE = join(SESSION_DIR, "tokens.json");
const TOKEN_ENDPOINT = `${OIDC.issuer}/protocol/openid-connect/token`;
const AUTH_ENDPOINT = `${OIDC.issuer}/protocol/openid-connect/auth`;
const EXPIRY_SKEW_MS = 60_000;
/** After a rejected login, do not try again for this long: Keycloak brute-force detection can lock the account. */
const LOGIN_COOLDOWN_MS = 10 * 60_000;

const b64u = (buf) => buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

export class AuthError extends Error {}

/**
 * ITMO ID (Keycloak) session for the my.itmo.ru SPA client.
 * Authorization Code + PKCE driven over plain HTTP — no browser needed.
 * Tokens are cached in SESSION_DIR/tokens.json (0600, gitignored) and refreshed with the refresh token.
 */
export class ItmoSession {
  #tokens = null;
  #inflight = null;
  #loginFailedAt = 0;
  #loginFailure = "";

  constructor() {
    this.#tokens = this.#readCache();
  }

  /** A valid access token, refreshing or logging in as needed. */
  async accessToken({ force = false } = {}) {
    const t = this.#tokens;
    if (!force && t && t.expiresAt - Date.now() > EXPIRY_SKEW_MS) return t.accessToken;
    this.#inflight ??= this.#renew(force).finally(() => (this.#inflight = null));
    return (await this.#inflight).accessToken;
  }

  /** Non-secret facts about the current session. */
  async whoami() {
    const token = await this.accessToken();
    const claims = JSON.parse(Buffer.from(token.split(".")[1], "base64url").toString());
    return {
      isu: claims.isu ?? null,
      email: claims.email ?? null,
      username: claims.preferred_username ?? null,
      scope: claims.scope,
      accessTokenExpiresAt: new Date(claims.exp * 1000).toISOString(),
      refreshTokenExpiresAt: this.#tokens?.refreshExpiresAt ? new Date(this.#tokens.refreshExpiresAt).toISOString() : null,
    };
  }

  logout() {
    this.#tokens = null;
    try {
      unlinkSync(TOKEN_FILE);
    } catch {
      /* already gone */
    }
  }

  async #renew(force) {
    const t = this.#tokens;
    if (t?.refreshToken && t.refreshExpiresAt - Date.now() > EXPIRY_SKEW_MS) {
      try {
        return this.#store(await this.#tokenRequest({ grant_type: "refresh_token", refresh_token: t.refreshToken, client_id: OIDC.clientId }));
      } catch {
        /* refresh token revoked or session ended — fall through to a full login */
      }
    }
    return this.#login();
  }

  async #login() {
    if (this.#loginFailedAt && Date.now() - this.#loginFailedAt < LOGIN_COOLDOWN_MS) {
      throw new AuthError(`Login is paused for 10 minutes after a failed attempt (${this.#loginFailure}). Fix .env credentials and restart the MCP server.`);
    }
    const env = loadEnv();
    if (!env.MY_ITMO_EMAIL || !env.MY_ITMO_PASSWORD) {
      throw new AuthError("MY_ITMO_EMAIL and MY_ITMO_PASSWORD must be set in the project .env (see .env.example).");
    }
    try {
      return this.#store(await this.#passwordFlow(env.MY_ITMO_EMAIL, env.MY_ITMO_PASSWORD));
    } catch (err) {
      if (err instanceof AuthError) {
        this.#loginFailedAt = Date.now();
        this.#loginFailure = err.message;
      }
      throw err;
    }
  }

  async #passwordFlow(username, password) {
    const jar = new Map();
    const hop = async (url, init = {}) => {
      for (let i = 0; i < 12; i++) {
        const res = await fetch(url, {
          ...init,
          redirect: "manual",
          signal: AbortSignal.timeout(30_000),
          headers: { cookie: [...jar].map(([k, v]) => `${k}=${v}`).join("; "), ...init.headers },
        });
        for (const c of res.headers.getSetCookie()) {
          const [kv] = c.split(";");
          const eq = kv.indexOf("=");
          jar.set(kv.slice(0, eq).trim(), kv.slice(eq + 1));
        }
        const loc = res.headers.get("location");
        if (res.status >= 300 && res.status < 400 && loc) {
          const next = new URL(loc, url).toString();
          if (next.startsWith(OIDC.redirectUri)) return { callback: new URL(next) };
          url = next;
          init = {};
          continue;
        }
        return { res, url };
      }
      throw new AuthError("Too many redirects during login.");
    };

    const verifier = b64u(randomBytes(32));
    const state = b64u(randomBytes(12));
    const authUrl = new URL(AUTH_ENDPOINT);
    authUrl.search = new URLSearchParams({
      response_type: "code",
      client_id: OIDC.clientId,
      redirect_uri: OIDC.redirectUri,
      scope: OIDC.scope,
      state,
      code_challenge: b64u(createHash("sha256").update(verifier).digest()),
      code_challenge_method: "S256",
    }).toString();

    const first = await hop(authUrl.toString());
    if (first.callback) return this.#exchange(first.callback, state, verifier); // already SSO-authenticated
    const page = await first.res.text();

    // The Keycloak theme renders client-side; the form target is inside the kcContext object. Read it as data, never evaluate it.
    const action = page.match(/"loginAction"\s*:\s*("(?:[^"\\]|\\.)*")/);
    if (!action) throw new AuthError("ITMO ID login page layout changed: loginAction not found.");
    const second = await hop(JSON.parse(action[1]), {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username, password, credentialId: "" }).toString(),
    });
    if (!second.callback) {
      const body = await second.res.text();
      const pageId = body.match(/"pageId"\s*:\s*"([^"]+)"/)?.[1] ?? "unknown";
      const summary = body.match(/"summary"\s*:\s*("(?:[^"\\]|\\.)*")/);
      const reason = summary ? JSON.parse(summary[1]) : "no message";
      throw new AuthError(`ITMO ID rejected the login (page: ${pageId}): ${reason}. 2FA/captcha/password-change screens cannot be automated.`);
    }
    return this.#exchange(second.callback, state, verifier);
  }

  async #exchange(callbackUrl, state, verifier) {
    const err = callbackUrl.searchParams.get("error");
    if (err) throw new AuthError(`ITMO ID returned an error: ${err} ${callbackUrl.searchParams.get("error_description") ?? ""}`);
    if (callbackUrl.searchParams.get("state") !== state) throw new AuthError("OIDC state mismatch.");
    return this.#tokenRequest({
      grant_type: "authorization_code",
      code: callbackUrl.searchParams.get("code"),
      client_id: OIDC.clientId,
      redirect_uri: OIDC.redirectUri,
      code_verifier: verifier,
    });
  }

  async #tokenRequest(params) {
    const res = await fetch(TOKEN_ENDPOINT, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams(params).toString(),
      signal: AbortSignal.timeout(30_000),
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok || !json.access_token) throw new Error(`Token endpoint ${res.status}: ${json.error_description ?? json.error ?? "unknown error"}`);
    return json;
  }

  #store(json) {
    const now = Date.now();
    this.#tokens = {
      accessToken: json.access_token,
      refreshToken: json.refresh_token,
      expiresAt: now + json.expires_in * 1000,
      refreshExpiresAt: now + (json.refresh_expires_in ?? 0) * 1000,
    };
    try {
      mkdirSync(SESSION_DIR, { recursive: true, mode: 0o700 });
      const tmp = `${TOKEN_FILE}.${process.pid}.tmp`;
      writeFileSync(tmp, JSON.stringify(this.#tokens), { mode: 0o600 });
      renameSync(tmp, TOKEN_FILE);
      chmodSync(TOKEN_FILE, 0o600);
    } catch {
      /* cache is an optimisation only */
    }
    return this.#tokens;
  }

  #readCache() {
    try {
      if (!existsSync(TOKEN_FILE)) return null;
      const t = JSON.parse(readFileSync(TOKEN_FILE, "utf8"));
      return t?.accessToken ? t : null;
    } catch {
      return null;
    }
  }
}
