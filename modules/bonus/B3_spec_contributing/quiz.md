# Quiz

1. What is the normative field source?
<details><summary>Answer</summary>The versioned a2a.proto, interpreted alongside binding and behavioral requirements.</details>

2. How do you report a conformance contradiction?
<details><summary>Answer</summary>Capture the smallest request/response, identify the exact requirement and test revision, and retain the raw result.</details>

3. Does schema parsing prove behavior?
<details><summary>Answer</summary>No. A parseable response can still violate ownership, state transitions or required transport semantics.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Locate a protobuf field: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>Read the normative protobuf alongside binding rules and behavioral requirements. A field being parseable does not make a behavior conformant. Reduce a suspected bug to a captured request, observed response and specific requirement. Distinguish a documentation typo from a change to the protocol contract.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
