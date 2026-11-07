# Why it works

HTTP routes differ from JSON-RPC method strings; protobuf annotations define the mapping.

JSON-RPC, HTTP+JSON and gRPC map the same abstract operations onto different transports. ProtoJSON gives the JSON forms of protobuf messages. gRPC uses generated stubs and binary protobuf over HTTP/2. The offline service harness serializes and deserializes protobuf and calls the real SDK servicer; it does not test HTTP/2 framing. Select the advertised interface, not a URL guessed from another binding.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
