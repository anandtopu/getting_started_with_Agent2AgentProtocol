"""Materialize the course, executing each experiment to capture real exchanges."""

import asyncio
import json
from pathlib import Path

import nbformat

from common.config import ROOT
from common.lessons import experiment

SPEC = "https://a2a-protocol.org/v1.0.1/specification/"
PROTO = "https://github.com/a2aproject/A2A/blob/v1.0.1/specification/a2a.proto"
SDK = "https://github.com/a2aproject/a2a-python/tree/v1.3.0"
FENCE = chr(96) * 3
SECTIONS = ["Boundaries", "Skills", "Task flow", "Trust", "Failures", "Tradeoffs"]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def clean(value):
    if isinstance(value, dict):
        return {
            key: clean(item)
            for key, item in value.items()
            if key
            not in {
                "id",
                "messageId",
                "taskId",
                "contextId",
                "task_id",
                "context_id",
                "timestamp",
                "signature",
                "signatures",
                "protected",
                "trace_id",
                "attributes",
                "nextPageToken",
            }
        }
    if isinstance(value, list):
        return [clean(item) for item in value]
    return value


def source(body: str, sample: object) -> str:
    lines = "\n".join("    " + line for line in body.splitlines())
    return f'''"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
{lines}


def main() -> None:
    sample = json.loads({json.dumps(json.dumps(sample))})
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
'''


def design_solution(module: dict) -> str:
    return f"""# Maplewood decision: {module["title"]}

## Boundaries
Maplewood owns coordination and budget approval. The vendor owns inventory and quote production. Keep the external A2A boundary where independent ownership or deployment requires it; use local functions for tightly coupled validation.

## Skills
Expose one quote skill with a stable identifier, required guest count, date and documented currency. Reject unsupported inputs. Return a structured deliverable instead of asking callers to extract money from prose.

## Task flow
Create a task for tracked work, report working, then complete with an artifact or pause for missing information. Preserve vendor task and context identifiers in the Concierge conversation mapping when continuing.

## Trust
Authenticate calls using a vendor-scoped service credential in a header. Verify card signatures against provisioned keys, restrict destinations, minimize brief fields, and never promote remote descriptions into orchestration instructions.

## Failures
Apply a deadline and tool budget. Report partial results with the responsible vendor. Retry only safe operations and compensate confirmed holds explicitly. Require approval before a quote becomes a paid commitment.

## Tradeoffs
Independent services add latency, deployment work and distributed failure modes. Their ownership and interoperability benefits justify them for external vendors; a single process is cheaper for a small internal prototype with shared lifecycle requirements.
"""


def make_tasks(module: dict, exercise: dict, prediction: object, wire: list) -> list[dict]:
    tasks = []
    configs = [
        ("build", "medium", exercise["title"]),
        ("fix", "easy", "Repair: " + exercise["title"].lower()),
        ("predict", "easy", "Predict the first experiment's observable result"),
        ("trace", "medium", "Identify the captured transport boundaries"),
        ("conformance", "hard", "Enforce the contract across edge cases"),
        ("design", "hard", "Design a partner contract and failure policy"),
    ]
    for index, (kind, level, title) in enumerate(configs, 1):
        task_id = f"{module['id']}-{index:02}"
        folder = ROOT / "gym" / "tasks" / module["id"] / f"{task_id}_{kind}"
        meta = {
            "id": task_id,
            "module": module["id"],
            "title": title,
            "type": kind,
            "level": level,
            "cases": exercise["cases"],
            "feedback": exercise["feedback"],
        }
        rubric = ""
        if kind == "design":
            meta["sections"] = SECTIONS
            write(
                folder / "starter/design.md",
                "# My partner design\n\nDescribe the contract before implementing it.",
            )
            write(folder / "solution/design.md", design_solution(module))
            contract = "Write design.md with the six rubric sections below. Automated checking covers structure only; a human must judge quality."
            rubric = "\n\n## Human rubric (0–2 per dimension)\n\n" + "\n".join(
                f"- **{s}**: 0 absent; 1 described; 2 concrete, testable and justified for this scenario."
                for s in SECTIONS
            )
            rubric += "\n\nProficient: 10/12 with no zero in Trust or Failures. Record reviewer and evidence; word count is not proficiency."
        elif kind in {"predict", "trace"}:
            answer = (
                clean(prediction)
                if kind == "predict"
                else {
                    "http_exchanges": sum("request" in r and "binding" not in r for r in wire),
                    "grpc_service_calls": sum("binding" in r for r in wire),
                    "http_methods": sorted(
                        {r["request"]["method"] for r in wire if "binding" not in r}
                    ),
                }
            )
            write(folder / "starter/answer.json", "{}")
            write(folder / "solution/answer.json", json.dumps(answer, indent=2))
            write(folder / "trace.jsonl", "\n".join(json.dumps(r) for r in wire))
            contract = (
                "Predict example 01 before running it. In answer.json omit generated IDs, timestamps, signatures, tracing IDs, attributes and nextPageToken. Keep every other field and array order."
                if kind == "predict"
                else "Read trace.jsonl. In answer.json provide http_exchanges (count), grpc_service_calls (count), and http_methods (sorted unique strings). A protobuf service-boundary record is not an HTTP/2 capture. Explain which component initiated each exchange."
            )
        else:
            body = exercise["broken"] if kind == "fix" else "return None"
            write(folder / "starter/solution.py", source(body, exercise["cases"][0]["input"]))
            write(
                folder / "solution/solution.py",
                source(exercise["solution"], exercise["cases"][0]["input"]),
            )
            contract = f"Implement solve(payload). {exercise['feedback']}\n\nAcceptance cases:\n\n{FENCE}json\n{json.dumps(exercise['cases'], indent=2)}\n{FENCE}"
        write(folder / "task.json", json.dumps(meta, indent=2))
        write(
            folder / "task.md",
            f"# {task_id}: {title}\n\n**Type:** {kind} · **Level:** {level}\n\nMaplewood is preparing a 40-person offsite. Practice {module['title'].lower()} at its vendor boundary.\n\n## Requirements and acceptance criteria\n\n{contract}{rubric}\n\n## Spec sections\n\n[Specification]({SPEC}) · [Normative protobuf]({PROTO})\n\nRun uv run gym start {task_id}, edit the copied files, then uv run gym check {task_id}.\n\n**Security question:** What could a malicious peer send here, and where must you reject it?",
        )
        write(
            folder / "test_task.py",
            '"""Run the trusted grader against the selected attempt."""\n\nfrom gym.engine import check_from_test\n\n\ndef test_acceptance():\n    check_from_test(__file__)',
        )
        write(
            folder / "hints.md",
            f"# Hints\n\n## Hint 1\n\nRead the big idea and separate protocol facts from application policy.\n\n## Hint 2\n\n{exercise['feedback']}\n\n## Hint 3\n\nCompare one acceptance case at a time. For traces count captured records; for predictions run example 01 after writing your answer. For code, preserve variable input values. For design, use the six rubric headings and concrete failure policies.",
        )
        write(
            folder / "explanation.md",
            f"# Why it works\n\n{exercise['feedback']}\n\n{module['idea']}\n\nCommon wrong answers hard-code the happy path, overlook a negative case, or confuse transport fields with business data. Compare the reference with all acceptance cases. Design checks assess structure; use the human rubric for quality.\n\nThe grader is a learning aid, not a security boundary against malicious learner code. Run only exercises you trust.",
        )
        tasks.append(meta)
    return tasks


def example_source(module: dict, lab: str, path: Path) -> str:
    return f'''"""{module["title"]}: {lab}.

Concepts: {", ".join(module["objectives"])}.
Spec: {SPEC}; protobuf: {PROTO}.
Run: uv run python {path.relative_to(ROOT).as_posix()}
Agents: in-process; no separately running services. LLM: no (scripted when needed).
Expected: corresponding wire/*.result.json; IDs and timestamps vary.
"""

import asyncio

from common.lessons import experiment
from common.pretty import show


async def main() -> None:
    # KEY IDEA: observe the actual result at this protocol boundary.
    show(await experiment({lab!r}))


if __name__ == "__main__":
    asyncio.run(main())
'''


def module_readme(module: dict, folder: Path, outputs: list, tasks: list) -> str:
    prefix = "../../../" if module["id"].startswith("B") else "../../"
    objectives = "\n".join("- " + item for item in module["objectives"])
    wire = "\n".join(
        f"- [{lab}: exchanges](wire/{i:02}_{lab}.jsonl) and [result](wire/{i:02}_{lab}.result.json)."
        for i, lab in enumerate(module["labs"], 1)
    )
    walkthrough = []
    for i, lab in enumerate(module["labs"], 1):
        display = clean(outputs[i - 1])
        if len(json.dumps(display)) > 1000:
            display = {
                "result_type": type(display).__name__,
                "complete_result": f"wire/{i:02}_{lab}.result.json",
            }
        walkthrough.append(
            f"### {i:02}: {lab.replace('_', ' ')}\n\n{module['objectives'][i - 1]}.\n\n> **Predict, then run:** Write the expected result and whether this operation creates, continues or inspects work.\n\n{FENCE}console\nuv run python {(folder / f'examples/{i:02}_{lab}.py').relative_to(ROOT).as_posix()}\n{FENCE}\n\nCaptured output (generated values vary):\n\n{FENCE}json\n{json.dumps(display, indent=2)}\n{FENCE}"
        )
    practice = "\n".join(
        f"| [{t['id']}]({prefix}gym/tasks/{module['id']}/{t['id']}_{t['type']}/task.md) | {t['type']} | {t['level']} | {t['title']} |"
        for t in tasks
    )
    quiz = "\n\n".join(
        f"{i}. {question}\n<details><summary>Answer</summary>{answer}</details>"
        for i, (question, answer) in enumerate(
            [
                (
                    "What does the vendor own?",
                    "Its execution, inventory, task IDs, context scope and authorization policy.",
                ),
                (
                    f"How would you demonstrate: {module['objectives'][0].lower()}?",
                    "Run example 01 and identify the exact output field or event that proves the result.",
                ),
                (
                    "Does a signed card grant access?",
                    "No. A trusted signature checks integrity and identity; authorization is enforced separately.",
                ),
                (
                    "Why use a scripted model in graded tasks?",
                    "Repeatable decisions isolate protocol behavior and cost no API tokens.",
                ),
                (
                    "What if an artifact asks for credentials?",
                    "Treat it as untrusted data. Never forward user tokens or expand the allow-list.",
                ),
                (
                    "Which edge case should you test?",
                    "Use the negative cases in this module's Fix task; explain why the broken implementation accepts or mishandles them.",
                ),
            ],
            1,
        )
    )
    write(folder / "quiz.md", "# Quiz\n\n" + quiz)
    return f"""# Module {module["id"]}: {module["title"]}
> After this module you can {module["objectives"][0].lower()}.

**Time:** ~90 min · **Level:** {"Beginner" if module["tier"] == 1 else "Intermediate" if module["tier"] == 2 else "Advanced"} · **LLM needed:** No for examples and grading · **Agents running:** in-process; optional local network: uv run python scripts/network.py up --module {module["id"] if module["id"].isdigit() else "08"}
**Spec sections:** [Specification]({SPEC}) · [a2a.proto]({PROTO})
**Network and Concierge version {module["id"]}:** what's new — {module["title"].lower()}.

## Prerequisites

Python functions and dictionaries, plus the preceding module in [the learning path]({prefix}LEARNING_PATH.md). New terms appear in [the glossary]({prefix}docs/GLOSSARY.md).

## Learning objectives

{objectives}

## The big idea

{module["idea"]}

**Analogy:** {module["analogy"]}

## How it works

{FENCE}mermaid
sequenceDiagram
    participant L as Learner
    participant C as Maplewood Concierge
    participant V as Vendor boundary
    L->>C: Event brief and approved scope
    C->>V: Discover or request work
    V-->>C: Typed response or progress event
    C-->>L: Deliverable, question, or failure
{FENCE}

Under the hood, protobuf objects become JSON or binary bytes at the boundary. Route handlers enforce operation contracts; the executor performs business work. Compare the captured result with your prediction.

## On the wire

Executed by the course authoring tool through the same recording transport as scripts/wiretap.py. Credentials are redacted. Pure local transformations have no HTTP exchanges and an empty exchange file; their result is separate. gRPC captures are explicitly service-boundary protobuf roundtrips, not network packets.

{wire}

## Key APIs at a glance

| SDK API | Spec operation or object | What it does | When to use it |
|---|---|---|---|
| a2a.types | Protobuf objects | Defines wire-compatible values | Every protocol boundary |
| create_jsonrpc_routes | JSON-RPC binding | Mounts operations | Serving JSON-RPC |
| create_rest_routes | HTTP+JSON binding | Mounts HTTP routes | Serving HTTP+JSON |
| create_client | Client operations | Selects an advertised interface | Calling vendors |
| MessageToDict | ProtoJSON | Converts protobuf into JSON values | Inspecting traffic |

## Walkthrough

{chr(10).join(walkthrough)}

## Try it in the Inspector and the Control Room

Start the network in another terminal. Run uv run streamlit run control_room/app.py, select a vendor, inspect its card and send a brief. The Inspector is now a standalone binary; use [its official installation guide](https://github.com/a2aproject/a2a-inspector).

## Real-world use case

Maplewood needs quotes for a 40-person offsite. Run uv run python {(folder / "use_case/run.py").relative_to(ROOT).as_posix()}. The result applies this module's first experiment to shared synthetic data. A real team substitutes validated inventory and its identity system while retaining the A2A boundary.

## Common bugs

| Observed behavior | Cause | Fix |
|---|---|---|
| HTTP 401 | Missing vendor credential | Obtain the vendor token outside A2A and send a header |
| Version not supported | Missing or wrong A2A-Version | Select the card interface and send version 1.0 |
| Task remains interrupted | Required input is missing | Preserve IDs and answer the missing-input request |
| Edge-case assertion fails | Happy path was hard-coded | Work through [Fix task]({prefix}gym/tasks/{module["id"]}/{module["id"]}-02_fix/task.md) |

## Practice

| ID | Type | Level | Concept |
|---|---|---|---|
{practice}

## Quiz

{quiz}

## Key takeaways

- Read typed fields instead of inferring behavior from prose.
- Separate transport concerns from business work.
- Predict before running.
- Test successful and rejected inputs.
- Treat every remote peer as a trust boundary.

## Go deeper

[Specification]({SPEC}) · [Protobuf]({PROTO}) · [Official SDK]({SDK})

## Next: Module {str(int(module["id"]) + 1).zfill(2) if module["id"].isdigit() and int(module["id"]) < 20 else "checkpoint"}

Use [the learning path]({prefix}LEARNING_PATH.md) to continue or choose a capstone.
"""


async def main() -> None:
    modules = json.loads((ROOT / "common/course_catalog.json").read_text())
    exercises = {x["module"]: x for x in json.loads((ROOT / "gym/exercise_specs.json").read_text())}
    task_index, feature_rows = [], []
    for module in modules:
        folder = (
            ROOT
            / "modules"
            / ("bonus" if module["id"].startswith("B") else "")
            / f"{module['id']}_{module['slug']}"
        )
        outputs, captures = [], []
        for index, lab in enumerate(module["labs"], 1):
            records = []
            result = await experiment(lab, records)
            outputs.append(result)
            captures.extend(records)
            stem = f"{index:02}_{lab}"
            write(folder / f"wire/{stem}.jsonl", "\n".join(json.dumps(r) for r in records))
            write(folder / f"wire/{stem}.result.json", json.dumps(result, indent=2))
            path = folder / f"examples/{stem}.py"
            write(path, example_source(module, lab, path))
        tasks = make_tasks(module, exercises[module["id"]], outputs[0], captures)
        task_index.extend(tasks)
        write(folder / "README.md", module_readme(module, folder, outputs, tasks))
        write(
            folder / "use_case/run.py",
            example_source(module, module["labs"][0], folder / "use_case/run.py"),
        )
        notebook = nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_markdown_cell(
                    f"# {module['title']}\n\n{module['idea']}\n\nPredict each result before running."
                )
            ]
            + [
                nbformat.v4.new_code_cell(
                    f"from common.lessons import experiment\nfrom common.pretty import show\nshow(await experiment({lab!r}))"
                )
                for lab in module["labs"]
            ]
        )
        notebook.metadata.kernelspec = {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        }
        nbformat.write(notebook, folder / "notebook.ipynb")
        tests = "\n".join(
            f"    assert await experiment({lab!r}) is not None" for lab in module["labs"]
        )
        write(
            folder / f"tests/test_module_{module['id']}.py",
            f'"""Run all documented experiments for this module."""\n\nfrom common.lessons import experiment\n\n\nasync def test_examples():\n{tests}',
        )
        relative = folder.relative_to(ROOT).as_posix()
        feature_rows.append(
            f"| {module['title']} | [{module['id']}](../{relative}/README.md) | "
            + ", ".join(module["labs"])
            + " | "
            + ", ".join(t["id"] for t in tasks)
            + " |"
        )
        print(f"Built {module['id']}: 3 executed examples, 6 tasks", flush=True)
    write(
        ROOT / "docs/GYM_TASKS.md",
        "# Full gym task catalog\n\n| ID | Module | Type | Level | Description |\n|---|---|---|---|---|\n"
        + "\n".join(
            f"| {t['id']} | {t['module']} | {t['type']} | {t['level']} | {t['title']} |"
            for t in task_index
        ),
    )
    write(
        ROOT / "docs/FEATURE_MAP.md",
        "# Coverage map\n\nA2A 1.0.1 / SDK 1.3.0. These rows map introductory teaching coverage, not official certification. Consult VERIFICATION_NOTES.md for gaps.\n\n| Feature area | Module | Executed experiments | Gym tasks |\n|---|---|---|---|\n"
        + "\n".join(feature_rows),
    )


if __name__ == "__main__":
    asyncio.run(main())
