# Quiz

1. Does gRPC use SSE frames?
<details><summary>Answer</summary>No. It streams typed protobuf messages over its service transport.</details>

2. Which names define the operations?
<details><summary>Answer</summary>The A2AService methods in the normative versioned a2a.proto.</details>

3. Can one card advertise several bindings?
<details><summary>Answer</summary>Yes. Each supported interface includes its own URL, binding and protocol version.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Compare equivalent calls: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>JSON-RPC, HTTP+JSON and gRPC map the same abstract operations onto different transports. ProtoJSON gives the JSON forms of protobuf messages. gRPC uses generated stubs and binary protobuf over HTTP/2. The offline service harness serializes and deserializes protobuf and calls the real SDK servicer; it does not test HTTP/2 framing. Select the advertised interface, not a URL guessed from another binding.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
