/** Authenticated Inkwell quote server. Run npm run vendor after setting MAPLEWOOD_TOKEN.
 * Uses A2A 1.0 SendMessage and task/artifact events; no model is required.
 */
import express from "express";
import { timingSafeEqual } from "node:crypto";
import { AgentCard, Task, TaskArtifactUpdateEvent, TaskStatusUpdateEvent } from "@a2a-js/sdk";
import { AgentEvent, DefaultRequestHandler, InMemoryTaskStore } from "@a2a-js/sdk/server";
import type { AgentExecutor, ExecutionEventBus, RequestContext } from "@a2a-js/sdk/server";
import { agentCardHandler, jsonRpcHandler, restHandler } from "@a2a-js/sdk/server/express";

const token = process.env.MAPLEWOOD_TOKEN;
if (!token) throw new Error("Set MAPLEWOOD_TOKEN before starting this server.");
const port = Number(process.env.MAPLEWOOD_TS_PORT ?? "8304");
const base = "http://127.0.0.1:" + port;
const card = AgentCard.fromJSON({
  name: "Inkwell Print Co. TypeScript",
  description: "Quote recycled event badges at 250 cents each; no purchase.",
  version: "1.0.0",
  supportedInterfaces: [
    { url: base + "/rpc", protocolBinding: "JSONRPC", protocolVersion: "1.0" },
    { url: base, protocolBinding: "HTTP+JSON", protocolVersion: "1.0" },
  ],
  capabilities: { streaming: true },
  defaultInputModes: ["application/json"],
  defaultOutputModes: ["application/json"],
  securitySchemes: { vendor: { httpAuthSecurityScheme: { scheme: "Bearer" } } },
  securityRequirements: [{ schemes: { vendor: { list: [] } } }],
  skills: [{ id: "print.quote", name: "Badge estimate", description: "Accept guests and return a quote in integer cents.", tags: ["printing"] }],
});

class Printer implements AgentExecutor {
  async execute(context: RequestContext, bus: ExecutionEventBus): Promise<void> {
    const taskId = context.taskId;
    const contextId = context.contextId;
    bus.publish(AgentEvent.task(Task.fromJSON({
      id: taskId, contextId, status: { state: "TASK_STATE_SUBMITTED" }, history: [],
    })));
    const part = context.userMessage.parts.find(p => p.content?.$case === "data");
    const data = part?.content?.$case === "data" ? part.content.value as Record<string, unknown> : {};
    const guests = data.guests;
    const valid = typeof guests === "number" && Number.isInteger(guests) && guests > 0 && guests <= 1000;
    if (valid) {
      bus.publish(AgentEvent.artifactUpdate(TaskArtifactUpdateEvent.fromJSON({
        taskId, contextId, lastChunk: true,
        artifact: { artifactId: "quote", name: "quote", parts: [{ data: {
          vendor: "print", selection: "badge", guests, total_cents: guests * 250,
          currency: "USD", approved: false,
        } }] },
      })));
    }
    bus.publish(AgentEvent.statusUpdate(TaskStatusUpdateEvent.fromJSON({
      taskId, contextId, status: { state: valid ? "TASK_STATE_COMPLETED" : "TASK_STATE_REJECTED" },
    })));
  }
  async cancelTask(taskId: string, bus: ExecutionEventBus): Promise<void> {
    bus.publish(AgentEvent.statusUpdate(TaskStatusUpdateEvent.fromJSON({
      taskId, status: { state: "TASK_STATE_CANCELED" },
    })));
  }
}

const handler = new DefaultRequestHandler(card, new InMemoryTaskStore(), new Printer());
const app = express();
app.use("/.well-known/agent-card.json", agentCardHandler({ agentCardProvider: handler }));
app.use((req, res, next) => {
  const supplied = Buffer.from(req.headers.authorization ?? "");
  const expected = Buffer.from("Bearer " + token);
  if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
    res.status(401).json({ error: "Vendor authentication required" });
    return;
  }
  next();
});
const userBuilder = async () => ({ isAuthenticated: true, userName: "maplewood:concierge" });
app.use("/rpc", jsonRpcHandler({ requestHandler: handler, userBuilder }));
app.use(restHandler({ requestHandler: handler, userBuilder }));
app.listen(port, "127.0.0.1", () => console.log("Inkwell ready at " + base));
