#!/usr/bin/env node
// Read-only MCP server (default). Mutating tools are not registered at all.
import { run } from "./src/server.js";

run({ write: false }).catch((err) => {
  console.error(err);
  process.exit(1);
});
