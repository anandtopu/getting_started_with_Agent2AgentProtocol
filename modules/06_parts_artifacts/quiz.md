# Quiz

1. What are the four Part content alternatives?
<details><summary>Answer</summary>Text, raw bytes, URL and structured data.</details>

2. How are bytes represented in ProtoJSON?
<details><summary>Answer</summary>As base64 text, with the media type carried separately.</details>

3. Can one Part contain both raw bytes and text?
<details><summary>Answer</summary>No. They are alternatives in the same content oneof.</details>

4. Can a quote artifact contain JSON and a PDF?
<details><summary>Answer</summary>Yes, as separate Parts of the same artifact.</details>

5. Why validate integer-valued ProtoJSON numbers?
<details><summary>Answer</summary>Struct numbers may round-trip as floats; whole-number business quantities still require validation.</details>

6. Why refuse redirects when fetching an approved file?
<details><summary>Answer</summary>A redirect can send the request to a private or otherwise unapproved destination.</details>
