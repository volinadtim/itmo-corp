#!/usr/bin/env node
/**
 * MCP server: my.itmo.ru via agent-browser CLI
 * Reads credentials from ITMO_CORP_ROOT/.env
 */

import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import dotenv from "dotenv";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "../../..");
const SESSION = "my-itmo";
const ENV_FILE = process.env.ITMO_CORP_ENV ?? join(PROJECT_ROOT, ".env");

if (existsSync(ENV_FILE)) {
  dotenv.config({ path: ENV_FILE });
}

function runScript(name, args = []) {
  const script = join(PROJECT_ROOT, "integrations/my-itmo/scripts", name);
  return new Promise((resolvePromise, reject) => {
    const child = spawn("bash", [script, ...args], {
      cwd: PROJECT_ROOT,
      env: { ...process.env, MY_ITMO_SESSION: SESSION },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));
    child.on("close", (code) => {
      if (code === 0) resolvePromise({ stdout, stderr });
      else reject(new Error(stderr || stdout || `exit ${code}`));
    });
  });
}

function runAgentBrowser(args) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(
      "npx",
      ["--yes", "agent-browser", "--session", SESSION, ...args],
      { cwd: PROJECT_ROOT, env: process.env }
    );
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));
    child.on("close", (code) => {
      const out = (stdout + stderr).trim();
      if (code === 0) resolvePromise(out);
      else reject(new Error(out || `agent-browser exit ${code}`));
    });
  });
}

const TOOLS = [
  {
    name: "my_itmo_login",
    description:
      "Log in to my.itmo.ru using credentials from .env (MY_ITMO_EMAIL, MY_ITMO_PASSWORD). Saves browser session for reuse. Call this first if my_itmo_status fails.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "my_itmo_status",
    description:
      "Check whether the my.itmo.ru session is active. Returns LOGGED_IN or NOT_LOGGED_IN plus page snapshot preview.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
  {
    name: "my_itmo_snapshot",
    description:
      "Get accessibility snapshot of current my.itmo.ru page (interactive elements with @refs). Optionally pass url to navigate first. Requires active session.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "Optional URL to open before snapshot (must be on *.itmo.ru)",
        },
      },
      required: [],
    },
  },
  {
    name: "my_itmo_open",
    description:
      "Open a URL in authenticated my.itmo.ru session and return page snapshot. Use for navigating to applications, my requests, etc.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "Full URL on my.itmo.ru or id.itmo.ru",
        },
      },
      required: ["url"],
    },
  },
  {
    name: "my_itmo_open_applications",
    description:
      "Navigate to «Заявки и очереди» section and return snapshot of available application types.",
    inputSchema: { type: "object", properties: {}, required: [] },
  },
];

const server = new Server(
  { name: "my-itmo", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args = {} } = request.params;

  try {
    if (!existsSync(ENV_FILE)) {
      throw new Error(
        `.env not found at ${ENV_FILE}. Copy .env.example to .env and set MY_ITMO_EMAIL, MY_ITMO_PASSWORD.`
      );
    }

    let text = "";

    switch (name) {
      case "my_itmo_login": {
        const { stdout } = await runScript("login.sh");
        text = stdout;
        break;
      }
      case "my_itmo_status": {
        try {
          const { stdout } = await runScript("status.sh");
          text = stdout;
        } catch (e) {
          text = `NOT_LOGGED_IN\n${e.message}`;
        }
        break;
      }
      case "my_itmo_snapshot": {
        if (args.url) {
          await runScript("login.sh").catch(() => {});
          text = await runAgentBrowser(["open", args.url]);
          text += "\n" + (await runAgentBrowser(["wait", "--load", "networkidle"]).catch(() => ""));
        } else {
          await runScript("login.sh").catch(() => {});
        }
        text += await runAgentBrowser(["snapshot", "-i"]);
        break;
      }
      case "my_itmo_open": {
        if (!args.url) throw new Error("url is required");
        await runScript("login.sh").catch(() => {});
        await runAgentBrowser(["open", args.url]);
        await runAgentBrowser(["wait", "--load", "networkidle"]).catch(() => {});
        text = `url: ${await runAgentBrowser(["get", "url"])}\n\n`;
        text += await runAgentBrowser(["snapshot", "-i"]);
        break;
      }
      case "my_itmo_open_applications": {
        const { stdout } = await runScript("open-applications.sh");
        text = stdout;
        break;
      }
      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return { content: [{ type: "text", text }] };
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error: ${err.message}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(console.error);
