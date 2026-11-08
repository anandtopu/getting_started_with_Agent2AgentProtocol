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
its configured trusted clients. It sends only permitted event fields to the
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
actual free-model tool selection; hosted provider account calls remain optional and
were not made with user credentials. The same checker can run against a configured
hosted provider. Costs and quotas belong to that account; no graded exercise calls it.

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
