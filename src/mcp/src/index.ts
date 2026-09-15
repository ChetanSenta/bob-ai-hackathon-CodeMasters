#!/usr/bin/env node
/**
 * Mission Readiness MCP Server
 *
 * Exposes 4 tools to IBM Bob that proxy calls to the FastAPI backend:
 *   - get_fleet_readiness     GET /readiness/fleet
 *   - get_asset_detail        GET /readiness/asset/{asset_id}
 *   - get_failure_predictions GET /predict/failures
 *   - get_maintenance_plan    GET /maintenance/plan
 *
 * Transport: stdio (spawned as a child process by Bob)
 * Backend URL defaults to http://localhost:8000 — override with BACKEND_URL env var.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const BACKEND_URL = (process.env.BACKEND_URL ?? "http://localhost:8000").replace(/\/$/, "");

// ---------------------------------------------------------------------------
// HTTP helper — lightweight fetch wrapper with error surfacing
// ---------------------------------------------------------------------------
async function backendGet(path: string): Promise<string> {
  const url = `${BACKEND_URL}${path}`;
  let res: Response;
  try {
    res = await fetch(url, { signal: AbortSignal.timeout(15_000) });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(
      `Cannot reach backend at ${url}. Is the FastAPI server running? (${msg})\n` +
      `Run: uvicorn src.backend.main:app --port 8000`
    );
  }
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Backend returned ${res.status} for ${path}: ${body}`);
  }
  return res.text();
}

// ---------------------------------------------------------------------------
// MCP server
// ---------------------------------------------------------------------------
const server = new McpServer({
  name: "mission-readiness",
  version: "1.0.0",
});

// ---- Tool 1: Fleet readiness -----------------------------------------------
server.registerTool(
  "get_fleet_readiness",
  {
    description:
      "Retrieves the current readiness status for all 25 assets in the fleet. " +
      "Returns GREEN/AMBER/RED status, overall health scores, and a fleet summary " +
      "(total, GREEN count, AMBER count, RED count). " +
      "Call this for any question about overall fleet status, how many assets are ready, " +
      "or which assets have problems.",
    inputSchema: z.object({}),
  },
  async () => {
    try {
      const data = await backendGet("/readiness/fleet");
      return { content: [{ type: "text" as const, text: data }] };
    } catch (err) {
      return {
        content: [{ type: "text" as const, text: String(err) }],
        isError: true,
      };
    }
  }
);

// ---- Tool 2: Asset detail ---------------------------------------------------
server.registerTool(
  "get_asset_detail",
  {
    description:
      "Retrieves detailed readiness information for a specific asset. " +
      "Returns all component statuses, recent sensor readings, service history, " +
      "and an AI-generated explanation of any issues. " +
      "Call this when the user asks about a specific tail number or platform. " +
      "Extract the asset_id from the tail number: TAIL-AH04 → AH04, TAIL-UH03 → UH03.",
    inputSchema: z.object({
      asset_id: z
        .string()
        .describe(
          "The asset identifier (e.g. AH04, UH03, AW02, MB03). " +
          "Strip the 'TAIL-' prefix if the user provides a tail number."
        ),
    }),
  },
  async ({ asset_id }) => {
    try {
      const data = await backendGet(`/readiness/asset/${encodeURIComponent(asset_id)}`);
      return { content: [{ type: "text" as const, text: data }] };
    } catch (err) {
      return {
        content: [{ type: "text" as const, text: String(err) }],
        isError: true,
      };
    }
  }
);

// ---- Tool 3: Failure predictions -------------------------------------------
server.registerTool(
  "get_failure_predictions",
  {
    description:
      "Returns a ranked list of components predicted to fail before the next mission window, " +
      "sorted by urgency (CRITICAL first, then HIGH, then MEDIUM). " +
      "Each entry includes the asset, component, current metric value, threshold, " +
      "hours until mission, and recommended action. " +
      "Call this when asked about predicted failures, what will break, or mission risk.",
    inputSchema: z.object({}),
  },
  async () => {
    try {
      const data = await backendGet("/predict/failures");
      return { content: [{ type: "text" as const, text: data }] };
    } catch (err) {
      return {
        content: [{ type: "text" as const, text: String(err) }],
        isError: true,
      };
    }
  }
);

// ---- Tool 4: Maintenance plan ----------------------------------------------
server.registerTool(
  "get_maintenance_plan",
  {
    description:
      "Returns a prioritised list of maintenance tasks sorted by urgency and mission proximity. " +
      "Each task includes the asset, component, required action, estimated duration in hours, " +
      "hours available until the mission window, and the deadline. " +
      "Call this for maintenance scheduling, work orders, or prioritisation questions.",
    inputSchema: z.object({}),
  },
  async () => {
    try {
      const data = await backendGet("/maintenance/plan");
      return { content: [{ type: "text" as const, text: data }] };
    } catch (err) {
      return {
        content: [{ type: "text" as const, text: String(err) }],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Mission Readiness MCP server running on stdio");
}

main().catch((err) => {
  console.error("Fatal MCP server error:", err);
  process.exit(1);
});
