# Quiz

1. Where is extension support negotiated?
<details><summary>Answer</summary>The card declares the URI; the request A2A-Extensions header activates it, and output marks where it applies.</details>

2. What if a required extension is absent?
<details><summary>Answer</summary>Reject the request with the required-extension protocol error before executing business work.</details>

3. How should a breaking extension change be published?
<details><summary>Answer</summary>Use a new URI and document coexistence/migration; do not silently reinterpret the old contract.</details>

4. How do you prove the first learning objective?
<details><summary>Answer</summary>Declare an extension: run the first example, identify the response field or event, and compare it with the stored wire/result capture.</details>

5. What is the trust boundary in this lesson?
<details><summary>Answer</summary>An extension has a URI, a declaration in capabilities and request-time activation through A2A-Extensions. A required extension is a compatibility obligation. Version selection belongs to the advertised interface. The structured quote extension adds a schema for the deliverable; it must not redefine core task states. Preserve skill contracts or version them when behavior changes.</details>

6. What should you do before consulting the reference solution?
<details><summary>Answer</summary>Write a prediction, run the starter, explain its failing assertion, then implement the required behavior and rerun the grader. For Design tasks, also apply the human rubric.</details>
