# Quiz

1. Does changing binding change task meaning?
<details><summary>Answer</summary>No. It changes transport representation, not the lifecycle contract.</details>

2. Where are operation names defined?
<details><summary>Answer</summary>The normative a2a.proto service definition.</details>

3. Does Inkwell's discovery HTTP port accept SendMessage?
<details><summary>Answer</summary>No. Its advertised task binding is gRPC only.</details>

4. How does gRPC carry credentials and trace context?
<details><summary>Answer</summary>In request metadata, or client identity through mTLS where configured.</details>

5. Is a service-boundary capture a network packet trace?
<details><summary>Answer</summary>No. It proves protobuf serialization and handler behavior; socket tests prove network interoperability separately.</details>

6. What should a client do with unsupported bindings?
<details><summary>Answer</summary>Choose another compatible advertised interface or fail clearly.</details>
