# Quiz

1. Do SDK version numbers have to match across languages?
<details><summary>Answer</summary>No. The implemented protocol contract must be compatible.</details>

2. What does the .NET preview label imply?
<details><summary>Answer</summary>Its upstream API may change; pin it and retain interoperability tests.</details>

3. Does protobuf alone guarantee correct business behavior?
<details><summary>Answer</summary>No. State transitions, authorization and artifacts still need checks.</details>

4. Why run the same scenario in all languages?
<details><summary>Answer</summary>It reveals semantic differences hidden by language-specific types.</details>

5. What differs across operating systems?
<details><summary>Answer</summary>Runtime installation, process startup and filesystem or shell behavior can differ.</details>

6. What should an SDK migration preserve?
<details><summary>Answer</summary>Advertised interfaces, authorization rules and observable task semantics.</details>
