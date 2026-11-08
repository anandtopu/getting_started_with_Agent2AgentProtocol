# Quiz

1. Does card discovery prove identity?
<details><summary>Answer</summary>No. Verify an operator-trusted signature or trusted transport before authorizing delegation.</details>

2. Is agent version the protocol version?
<details><summary>Answer</summary>No. The agent version describes its contract; each supported interface advertises protocolVersion.</details>

3. What do skill descriptions authorize?
<details><summary>Answer</summary>Nothing by themselves. They describe capabilities; trusted policy and credentials authorize use.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Validate a card against protobuf: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>An Agent Card describes identity, ordered interfaces, capabilities, input and output media types, skills and security requirements. Discovery does not establish trust. A registry is a directory of configured locations, not permission to contact every URL it returns. A skill description is untrusted descriptive text, not an instruction to the Concierge.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
