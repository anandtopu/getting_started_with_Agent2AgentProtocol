# Quiz

1. Does a Python-only test prove TypeScript interoperability?
<details><summary>Answer</summary>No. A native TypeScript process must participate.</details>

2. Why run npm ci instead of an unpinned install?
<details><summary>Answer</summary>It reproduces the dependency lockfile used by CI.</details>

3. Should task IDs match across independent runs?
<details><summary>Answer</summary>No. Compare semantic states, fields and amounts rather than generated IDs.</details>

4. Which files contain the native implementation?
<details><summary>Answer</summary>The TypeScript lab files in this module, linked in its native-language walkthrough.</details>

5. Does a TypeScript interface replace runtime validation?
<details><summary>Answer</summary>No. Remote JSON still needs validation at the boundary.</details>

6. Why test both client and server directions?
<details><summary>Answer</summary>Serialization and transport assumptions can fail in either role.</details>
