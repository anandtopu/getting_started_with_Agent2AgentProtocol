"""Task discovery and grading. Test cases live outside the learner's editable workspace."""

import importlib.util
import json
import os
from pathlib import Path

from common.config import ROOT

TASKS = ROOT / "gym" / "tasks"


def catalog() -> list[dict]:
    results = []
    for path in sorted(TASKS.glob("*/*/task.json")):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        metadata["path"] = path.parent
        results.append(metadata)
    return results


def find(task_id: str) -> dict:
    matches = [task for task in catalog() if task["id"] == task_id]
    if len(matches) != 1:
        raise ValueError(f"Unknown task {task_id!r}. Run gym list.")
    return matches[0]


def grade(task_dir: Path, attempt: Path) -> None:
    meta = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    if meta["type"] == "design":
        text = (attempt / "design.md").read_text(encoding="utf-8")
        for heading in meta["sections"]:
            assert f"## {heading}" in text, (
                f"Add the section: {heading}. Use the rubric for a human quality review."
            )
            section = text.split(f"## {heading}", 1)[1].split("## ")[0].strip()
            assert len(section.split()) >= 20, (
                f"Explain {heading} with at least 20 words and concrete tradeoffs."
            )
        return
    if meta["type"] in {"predict", "trace"}:
        actual = json.loads((attempt / "answer.json").read_text(encoding="utf-8"))
        expected = json.loads((task_dir / "solution" / "answer.json").read_text(encoding="utf-8"))
        assert actual == expected, (
            f"Your answer {actual!r} does not match the observations. Use gym hint {meta['id']} and inspect the cited example."
        )
        return
    module_spec = importlib.util.spec_from_file_location("learner_attempt", attempt / "solution.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    if meta.get("harness") == "protocol":
        from gym.protocol_checks import run

        run(meta["check"], module)
        return
    for index, case in enumerate(meta["cases"], 1):
        actual = module.solve(case["input"])
        assert actual == case["expected"], (
            f"Case {index}: input={case['input']!r}; expected {case['expected']!r}, got {actual!r}. {meta['feedback']}"
        )


def check_from_test(test_file: str) -> None:
    task_dir = Path(test_file).resolve().parent
    attempt = Path(os.environ.get("GYM_ATTEMPT", str(task_dir / "starter"))).resolve()
    grade(task_dir, attempt)
