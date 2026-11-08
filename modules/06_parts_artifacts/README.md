**Network and Concierge version 06:** what's new — parts and artifacts.

# Module 06: Parts and artifacts
> After this module you can construct all four part alternatives.

**Time:** ~90 min · **Level:** Beginner · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module 06
**Spec sections:** [Specification](https://a2a-protocol.org/v1.0.1/specification/) · [a2a.proto](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto)

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path](../../LEARNING_PATH.md). New terms appear in [the glossary](../../docs/GLOSSARY.md).

## Learning objectives

- Construct all four part alternatives
- Validate a quote
- Block unsafe file destinations

## The big idea

A Part contains exactly one of text, raw bytes, a URL or structured data. Protobuf encodes raw bytes as base64 in JSON. A data Part holds a JSON value; integer-valued numbers may round-trip as floating point. Validate quantities and money at the boundary. Files referenced by URL need a separate safe fetching policy. Artifacts collect one or more parts into a named deliverable.

**Analogy:** An envelope can contain a note, an attachment, or a reference to an approved document.

Read the [feature companion](../../docs/FEATURE_DEEP_DIVES.md) for field semantics, failure cases and
the connection to the final deployment.

## How it works

```mermaid
sequenceDiagram
    Concierge->>Saffron: Brief requesting file outputs
    Saffron-->>Concierge: Quote artifact with data and PDF bytes
    Concierge->>Granite: Request floor plan
    Granite-->>Concierge: SVG file Part
```

Under the hood: Each Part selects one content alternative. Raw bytes become base64 in JSON; mediaType identifies the content format. An artifact may contain multiple Parts. A URL is a reference, not permission to fetch it: apply origin, address, redirect and size policies before consuming remote files.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

- [parts: exchanges](wire/01_parts.jsonl) and [result](wire/01_parts.result.json).
- [rest: exchanges](wire/02_rest.jsonl) and [result](wire/02_rest.result.json).
- [ssrf: exchanges](wire/03_ssrf.jsonl) and [result](wire/03_ssrf.result.json).

## Key APIs at a glance

| SDK API or labeled course helper | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| Part | Content unit | Selects text, raw bytes, URL or data | Represent each content kind |
| Artifact | Deliverable | Groups Parts under an artifact ID | Return quotes and files together |

## Walkthrough

### 01: parts

Construct all four part alternatives.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/06_parts_artifacts/examples/01_parts.py
```

Captured output (generated values vary):

```json
[
  {
    "text": "Floor plan"
  },
  {
    "raw": "c3ludGhldGljIGZsb29yIHBsYW4=",
    "filename": "plan.txt",
    "mediaType": "text/plain"
  },
  {
    "url": "https://maplewood.example/plan",
    "mediaType": "text/plain"
  },
  {
    "data": {
      "total_cents": 96000.0
    },
    "mediaType": "application/json"
  }
]
```
### 02: rest

Validate a quote.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/06_parts_artifacts/examples/02_rest.py
```

Captured output (generated values vary):

```json
{
  "task": {
    "status": {
      "state": "TASK_STATE_COMPLETED",
      "message": {
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "Quote ready; no money has been spent."
          }
        ]
      }
    },
    "artifacts": [
      {
        "artifactId": "quote",
        "name": "quote",
        "parts": [
          {
            "data": {
              "guests": 40.0,
              "vendor": "venues",
              "approved": false,
              "selection": "room-1",
              "total_cents": 80000.0,
              "currency": "USD"
            },
            "mediaType": "application/json"
          }
        ]
      }
    ],
    "history": [
      {
        "role": "ROLE_USER",
        "parts": [
          {
            "data": {
              "dietary": {
                "standard": 30.0,
                "vegan": 10.0
              },
              "guests": 40.0,
              "budget_cents": 1000000.0,
              "date": "2027-06-01"
            },
            "mediaType": "application/json"
          }
        ]
      },
      {
        "role": "ROLE_AGENT",
        "parts": [
          {
            "text": "venues: checking the brief"
          }
        ]
      }
    ],
    "metadata": {
      "brief": {
        "guests": 40.0,
        "dietary": {
          "standard": 30.0,
          "vegan": 10.0
        },
        "budget_cents": 1000000.0,
        "date": "2027-06-01"
      }
    }
  }
}
```
### 03: ssrf

Block unsafe file destinations.

> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.

```console
uv run python modules/06_parts_artifacts/examples/03_ssrf.py
```

Captured output (generated values vary):

```json
{
  "blocked": [
    "https://127.0.0.1/private",
    "https://169.254.169.254/latest"
  ]
}
```

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood separates a structured quote from its attachment representation before returning both to the planner.

Run:

```console
uv run python modules/06_parts_artifacts/use_case/run.py
```

Selected observed fields (see [the complete captured result](wire/01_parts.result.json) for the full output):

```json
{
  "total_cents": 96000.0
}
```

A real deployment retains this boundary while substituting its own approved inventory, identity provider and operating policy.

## Common bugs

| Observed behavior | Cause | Fix and related practice |
|---|---|---|
| Earlier Part content disappears | Two oneof alternatives assigned | Use separate Parts; [practice 06-02](../../gym/tasks/06/06-02_fix/task.md) |
| File displays as corrupt text | Base64 or media type mishandled | Keep bytes and the correct mediaType; [practice 06-20](../../gym/tasks/06/06-20_parts_floor_plan/task.md) |
| Private endpoint contacted | URL fetched without egress policy | Reject private addresses and redirects; [practice 06-03](../../gym/tasks/06/06-03_predict/task.md) |
| Quote accepted with negative amount | Schema validation skipped | Validate structured data before use; [practice 06-21](../../gym/tasks/06/06-21_parts_data/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
| [06-01](../../gym/tasks/06/06-01_build/task.md) | build | medium | Preserve binary files using ProtoJSON |
| [06-02](../../gym/tasks/06/06-02_fix/task.md) | fix | easy | Repair: preserve binary files using protojson |
| [06-03](../../gym/tasks/06/06-03_predict/task.md) | predict | easy | Predict the first experiment's observable result |
| [06-04](../../gym/tasks/06/06-04_trace/task.md) | trace | medium | Identify the captured transport boundaries |
| [06-05](../../gym/tasks/06/06-05_conformance/task.md) | conformance | hard | Enforce the contract across edge cases |
| [06-06](../../gym/tasks/06/06-06_design/task.md) | design | hard | Design a partner contract and failure policy |

### Full boundary exercises

- [06-20: Receive Granite's real image artifact](../../gym/tasks/06/06-20_parts_floor_plan/task.md)
- [06-21: Read and validate a structured quote](../../gym/tasks/06/06-21_parts_data/task.md)
- [06-22: Keep independent deliverables separate](../../gym/tasks/06/06-22_parts_artifact_ids/task.md)
- [06-23: Attach inline artwork as a raw Part](../../gym/tasks/06/06-23_parts_raw_input/task.md)
- [06-24: Negotiate supported file media types](../../gym/tasks/06/06-24_parts_unsupported/task.md)
- [06-25: Receive Saffron's data and PDF together](../../gym/tasks/06/06-25_parts_multi_part/task.md)

These tasks execute actual SDK routes, workflows, cryptographic checks or independent
database connections offline. Each starter must fail and each reference solution must pass.

## Quiz

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

## Key takeaways

- Text, raw bytes, URL and structured data.
- As base64 text, with the media type carried separately.
- No. They are alternatives in the same content oneof.
- Yes, as separate Parts of the same artifact.
- Struct numbers may round-trip as floats; whole-number business quantities still require validation.

## Go deeper

[Specification](https://a2a-protocol.org/v1.0.1/specification/) · [Protobuf](https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto) · [Official SDK](https://github.com/a2aproject/a2a-python/tree/v1.3.0)

## Next: Module 07

Use [the learning path](../../LEARNING_PATH.md) to continue or choose a capstone.

## Real vendor files

Run `uv run python modules/06_parts_artifacts/examples/04_vendor_files.py` to receive
a valid PDF quote and SVG floor plan. The PDF and structured quote share an artifact
with multiple Parts. Predict the ProtoJSON base64 representation before reading
[the captured exchange](wire/04_vendor_files.jsonl). Never execute received artwork.
