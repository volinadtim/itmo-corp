#!/usr/bin/env node
// Read + write MCP server. Mutating tools are dry-run unless called with confirm=true.
import { run } from "./src/server.js";

run({ write: true }).catch((err) => {
  console.error(err);
  process.exit(1);
});
