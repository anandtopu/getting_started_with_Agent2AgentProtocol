# Quiz

1. Which ID matches an RPC response to its request?
<details><summary>Answer</summary>The top-level JSON-RPC id, not messageId or task id.</details>

2. Where does SendMessage's message go?
<details><summary>Answer</summary>Inside params.message in a JSON-RPC request.</details>

3. Must every response create a task?
<details><summary>Answer</summary>No. An agent may reply with a direct Message when tracked work is unnecessary.</details>

4. What does contextId group?
<details><summary>Answer</summary>Related interactions; it does not authorize access to other tasks.</details>

5. Is an artifact the same as a status message?
<details><summary>Answer</summary>No. Artifacts are deliverables, while status messages explain progress or missing input.</details>

6. Why compare three bindings?
<details><summary>Answer</summary>To recognize the same operations despite different HTTP paths, envelopes and protobuf encoding.</details>
