import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ItmoSession } from "./auth.js";
import { ItmoClient } from "./client.js";
import { registerReadTools } from "./tools/read.js";
import { registerWriteTools } from "./tools/write.js";

/** @param {{write:boolean}} opts write=false → read-only server (no mutating tool is even registered) */
export async function run({ write }) {
  const session = new ItmoSession();
  const client = new ItmoClient(session);
  const server = new McpServer(
    { name: write ? "my-itmo-write" : "my-itmo", version: "2.0.0" },
    {
      instructions: write
        ? "ITMO student portal access with WRITE tools. Every mutating tool is a dry run unless confirm=true; never set confirm=true without the user's explicit approval of the exact action shown in the preview."
        : "Read-only ITMO student portal access (my.itmo.ru API + public itmo.ru timetable). Start with itmo_whoami / itmo_sitemap.",
    }
  );
  registerReadTools(server, { client, session });
  if (write) registerWriteTools(server, { client, session });
  await server.connect(new StdioServerTransport());
}
