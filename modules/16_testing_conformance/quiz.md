# Quiz

1. Does an in-process HTTP test need a listening port?
<details><summary>Answer</summary>No. ASGITransport calls the app in the same process.</details>

2. What does protobuf parsing alone fail to check?
<details><summary>Answer</summary>Behavioral rules such as task transitions and authorization.</details>

3. Why retain the raw TCK report?
<details><summary>Answer</summary>To distinguish actual passes from skips and documented upstream contradictions.</details>

4. Does green CI mean full official certification?
<details><summary>Answer</summary>No. Read the exact conformance scope and exceptions.</details>

5. How do you test reconnect after publisher loss?
<details><summary>Answer</summary>Persist the task and journal, then subscribe through a second handler.</details>

6. What makes a useful bug report?
<details><summary>Answer</summary>A minimal request, observed response, expected behavior and specific requirement reference.</details>
