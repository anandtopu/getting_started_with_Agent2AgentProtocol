# Quiz

1. How are raw file bytes represented in ProtoJSON?
<details><summary>Answer</summary>As base64 in raw, with filename and mediaType describing the content.</details>

2. Can an artifact contain both data and a PDF?
<details><summary>Answer</summary>Yes. Multiple Parts can represent different forms of the same deliverable.</details>

3. Is a signed file URL automatically safe?
<details><summary>Answer</summary>No. Enforce trusted destination, scheme, address, redirects, expiry and byte limits before fetching.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Construct all four part alternatives: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>A Part contains exactly one of text, raw bytes, a URL or structured data. Protobuf encodes raw bytes as base64 in JSON. A data Part holds a JSON value; integer-valued numbers may round-trip as floating point. Validate quantities and money at the boundary. Files referenced by URL need a separate safe fetching policy. Artifacts collect one or more parts into a named deliverable.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
