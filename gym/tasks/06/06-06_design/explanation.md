# Why it works

Binary content becomes base64 in JSON; keep the media type and filename.

A Part contains exactly one of text, raw bytes, a URL or structured data. Protobuf encodes raw bytes as base64 in JSON. A data Part holds a JSON value; integer-valued numbers may round-trip as floating point. Validate quantities and money at the boundary. Files referenced by URL need a separate safe fetching policy. Artifacts collect one or more parts into a named deliverable.

Common wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.

The grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.
