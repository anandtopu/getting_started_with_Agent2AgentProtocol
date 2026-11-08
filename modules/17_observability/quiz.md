# Quiz

1. What links spans across HTTP and gRPC?
<details><summary>Answer</summary>W3C trace context propagated in headers or metadata.</details>

2. Are task ID and trace ID interchangeable?
<details><summary>Answer</summary>No. A task can outlive a single request trace.</details>

3. Why avoid task IDs as metric labels?
<details><summary>Answer</summary>Each new ID creates another time series and unbounded cardinality.</details>

4. Can a successful HTTP span prove the quote is correct?
<details><summary>Answer</summary>No. Golden evaluation must check delegations, states and artifacts.</details>

5. What should be excluded from telemetry?
<details><summary>Answer</summary>Credentials, private reasoning and unnecessary personal event fields.</details>

6. Why preserve a recording span across the SDK boundary?
<details><summary>Answer</summary>A non-recording replacement can silently lose task and context attributes.</details>
