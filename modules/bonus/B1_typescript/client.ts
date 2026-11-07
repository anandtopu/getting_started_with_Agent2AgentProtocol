/** Official SDK client. Run npm run client while the TypeScript vendor is running. */
import { randomUUID } from "node:crypto";
import { SendMessageRequest } from "@a2a-js/sdk";
import { ClientFactory } from "@a2a-js/sdk/client";

const token = process.env.MAPLEWOOD_TOKEN;
if (!token) throw new Error("Set MAPLEWOOD_TOKEN to the vendor's credential.");
const base = "http://127.0.0.1:" + (process.env.MAPLEWOOD_TS_PORT ?? "8304");
const client = await new ClientFactory().createFromUrl(base);
const response = await client.sendMessage(SendMessageRequest.fromJSON({
  message: { messageId: randomUUID(), role: "ROLE_USER", parts: [{ data: { guests: 40 } }] },
}), { serviceParameters: { Authorization: "Bearer " + token, "A2A-Version": "1.0" } });
console.log(JSON.stringify(response, null, 2));
