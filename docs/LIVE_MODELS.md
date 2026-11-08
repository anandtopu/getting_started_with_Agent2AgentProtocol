# Use the configured model

The default lessons and gym need no model. For optional live calls, copy
.env.example to .env, choose LLM_PROVIDER and LLM_MODEL, and start the local network:

~~~console
uv run python scripts/network.py up --module 10 --llm
~~~

Ollama is the default provider. Start Ollama and pull the model named in your
.env before starting the network. For hosted providers, export the corresponding
API key into the terminal environment; the model helper does not read provider
keys from arbitrary incoming requests.

The catering agent uses a real LangGraph workflow to choose ask_dietary or
quote_menu, then calls its internal MCP kitchen tool. The Concierge verifies
vendor cards, provides their skill names/descriptions to the model and bounds the selection to
its configured trusted clients and the user's requested vendor scope. It sends only permitted event fields to the
model and remote vendors. Quotes use deterministic inventory arithmetic.

For the mixed-framework network, first install the workers described in
[the integration matrix](../integrations/README.md), then:

~~~console
uv run python scripts/network.py up --module 11 --frameworks --llm
~~~

Here the Concierge uses the live model; vendor framework workers use deterministic
fixtures. They do not inherit provider keys or partner credentials.

Predict first: what happens if the model returns a sixth vendor, a URL, duplicate
vendor names or a tool name that is not allowed? The boundary rejects the decision.
When a task pauses, continuation retains the original vendor choices and task IDs.

All four native tool-stream formats are tested with fragmented HTTP responses:
Ollama NDJSON, OpenAI Responses SSE, Anthropic tool-use SSE and Gemini streaming
function calls. Frames and partial arguments have separate 64 KB limits; repeated
provider envelopes have a 512 KB total wire limit. Calls have a
90-second deadline; only a complete schema-valid select_action call is accepted.
The executor emits bounded A2A progress updates and final artifacts without exposing
private model reasoning. Provider-native streaming and A2A streaming remain separate
layers with different framing and completion rules.

The model request explicitly asks for one routing tool call, not a generated menu.
Its HTTP read budget matches the 90-second overall model deadline. The live-network
launcher gives model-backed vendor calls 120 seconds so that the model can return
its bounded result or failure instead of being cut off by the five-second quote-demo
budget. The bound is still enforced; incomplete output never becomes a tool invocation.

~~~console
uv run python scripts/check_live_model.py
~~~

CI installs checksum-verified Ollama v0.40.15 and runs qwen2.5:3b on CPU. This proves
actual free-model tool selection. An authorized local OpenAI run with gpt-4o-mini
also passed all three acceptance scenarios on 2026-11-08: native streamed tool
selection, A2A/LangGraph/MCP completion and Concierge routing. See the
[credential-free evidence](evidence/openai-live-2026-11-08.json). This is a local
account check, not a hosted-provider CI job or a claim that every OpenAI model is
available to every account. Anthropic and Gemini live checks are deferred because
credentials are unavailable. Costs and quotas belong to the account; no graded
exercise calls it.

For the same OpenAI check in PowerShell, place the key only in ignored `.env`
(never the tracked `.env.example`) and run:

~~~powershell
$env:LLM_PROVIDER = "openai"
$env:LLM_MODEL = "gpt-4o-mini"
uv run --env-file .env --offline python scripts/check_live_model.py
~~~

`--env-file` explicitly loads the private key into this command's environment;
`--offline` applies to dependency resolution, not the authorized API requests.
The checker still uses its bounded calls and synthetic event brief. The
[backlog](reviews/ACTION_PLAN.md) records remaining optional provider checks.

The real OpenAI run exposed an unsupported `uniqueItems` schema keyword. The
OpenAI request now uses a copied schema without that keyword, while the complete
original schema still validates the returned arguments locally before any tool
or vendor executes. Duplicate vendor choices remain invalid; strict tool generation,
array limits, enum constraints and local validation are retained. This follows
OpenAI's documented [supported schema subset](https://developers.openai.com/api/docs/guides/structured-outputs#supported-schemas).

Official framing references: [OpenAI](https://developers.openai.com/api/docs/guides/function-calling),
[Ollama](https://docs.ollama.com/capabilities/streaming),
[Anthropic](https://platform.claude.com/docs/en/build-with-claude/streaming).

The default is [Qwen2.5 3B](https://ollama.com/library/qwen2.5:3b), listed by Ollama
as tool-capable. It is a non-reasoning model suited to these small routing decisions.
The earlier Qwen3 4B passed a direct call but exhausted the bounded token allowance
in the expanded end-to-end check. The course keeps its limits and rejects incomplete
output rather than treating truncation as a successful action. LLM_MODEL remains
configurable; changing it requires rerunning the live acceptance check.

Missing or extra argument keys permit one repair request within the same 90-second
deadline. The repair prompt identifies only the required structure; it does not
forward the model's rejected text as instructions. Unknown enum values, unsafe tool
names, incomplete streams and a second invalid structure still fail. No tool is
executed before validation, and unexpected fields are never silently discarded.

Each live-check attempt first clears `workspace/live-model.json`. Expected model
or configuration failures exit with status 1 and a short recovery message pointing
to `scripts/check_env.py`; provider response text and credentials are not printed.
The success report is written only after all three acceptance paths pass, so an
older successful attempt cannot masquerade as the current result. The separate
introductory JSON helper also caps replies at 512,000 decoded bytes and 45 seconds
total; native tool streaming retains the limits described above.
