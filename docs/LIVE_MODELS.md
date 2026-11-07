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
vendor cards, provides their skill IDs to the model and bounds the selection to
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

All four provider request/response formats are tested with mocked HTTP responses.
Live account access is optional and has not been verified by this release.
This implementation uses bounded JSON decisions; it does not claim provider-native
streamed function-call support. A2A task streaming is a separate protocol feature.
