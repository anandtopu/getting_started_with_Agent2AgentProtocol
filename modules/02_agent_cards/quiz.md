# Quiz

1. Does a valid protobuf card establish trust?
<details><summary>Answer</summary>No. Parsing checks structure; configured identity and key policy establish trust.</details>

2. Which version belongs to the wire interface?
<details><summary>Answer</summary>supportedInterfaces[].protocolVersion; the card's version describes the agent product.</details>

3. May a registry entry redirect credentials anywhere?
<details><summary>Answer</summary>No. Only operator-approved destinations receive credentials.</details>

4. Can a skill override default media modes?
<details><summary>Answer</summary>A skill can refine its supported input and output modes.</details>

5. What does an absent streaming capability mean?
<details><summary>Answer</summary>Do not assume the agent supports streaming operations.</details>

6. What happens when no binding is compatible?
<details><summary>Answer</summary>Fail clearly or choose another approved agent; do not combine fields from incompatible interfaces.</details>
