import { readFileSync } from "node:fs";
import { join } from "node:path";
import { SERVER_ROOT } from "./config.js";

const load = (name) => JSON.parse(readFileSync(join(SERVER_ROOT, "data", name), "utf8"));

export const sitemap = () => load("sitemap.json");
export const apiCatalog = () => load("api-catalog.json");

export function searchCatalog({ query, module, audience, method, onlyWorking, limit = 80 }) {
  const { endpoints, generatedAt } = apiCatalog();
  const q = query?.toLowerCase();
  const rows = endpoints.filter(
    (e) =>
      (!module || e.module === module) &&
      (!audience || e.audience === audience) &&
      (!method || e.method === method.toUpperCase()) &&
      (!onlyWorking || e.probe?.status === 200) &&
      (!q || e.path.toLowerCase().includes(q))
  );
  return {
    generatedAt,
    total: rows.length,
    modules: [...new Set(endpoints.map((e) => e.module))].sort(),
    endpoints: rows.slice(0, limit).map((e) => ({
      method: e.method,
      path: e.path,
      ...(e.query ? { query: e.query } : {}),
      audience: e.audience,
      ...(e.risk ? { risk: e.risk } : {}),
      ...(e.probe ? { liveStatus: e.probe.status } : {}),
    })),
    note: rows.length > limit ? `Showing ${limit} of ${rows.length}; narrow with query/module.` : undefined,
  };
}
