# Quiz

1. What should a client do with a direct Message result?
<details><summary>Answer</summary>Read the message; do not invent a task ID and poll it.</details>

2. Does a timeout prove the vendor did nothing?
<details><summary>Answer</summary>No. The request may have committed before its response was lost.</details>

3. Which header selects the current protocol?
<details><summary>Answer</summary>A2A-Version: 1.0 for these pinned interfaces.</details>

4. Can an interrupted task move to a backup server?
<details><summary>Answer</summary>No. Its identity and state belong to the original server.</details>

5. When is retrying a quote reasonable?
<details><summary>Answer</summary>When it is a read-only operation under a bounded deadline and retry policy.</details>

6. What should TaskNotFound change in the UI?
<details><summary>Answer</summary>Show that the referenced work cannot be retrieved; do not report a successful quote.</details>
