import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));

export const SERVER_ROOT = resolve(here, "..");
export const PROJECT_ROOT = resolve(SERVER_ROOT, "../../..");
export const SESSION_DIR = process.env.ITMO_SESSION_DIR ?? join(PROJECT_ROOT, "integrations/my-itmo/.session");
export const ENV_FILE = process.env.ITMO_CORP_ENV ?? join(PROJECT_ROOT, ".env");

export const OIDC = {
  issuer: "https://id.itmo.ru/auth/realms/itmo",
  clientId: "student-personal-cabinet",
  redirectUri: "https://my.itmo.ru/login/callback",
  scope: "openid profile",
};
export const BASE_URL = "https://my.itmo.ru";
export const MAX_CHARS = Number(process.env.ITMO_MCP_MAX_CHARS) || 60_000;

/** Minimal .env parser. dotenv is avoided on purpose: newer versions log to stdout, which breaks MCP stdio. */
export function loadEnv() {
  const out = {};
  if (existsSync(ENV_FILE)) {
    for (const raw of readFileSync(ENV_FILE, "utf8").split(/\r?\n/)) {
      const line = raw.trim();
      if (!line || line.startsWith("#")) continue;
      const eq = line.indexOf("=");
      if (eq < 1) continue;
      let val = line.slice(eq + 1).trim();
      if (/^(".*"|'.*')$/.test(val)) val = val.slice(1, -1);
      out[line.slice(0, eq).trim()] = val;
    }
  }
  return { ...out, ...Object.fromEntries(Object.entries(process.env).filter(([k]) => k.startsWith("MY_ITMO_"))) };
}
