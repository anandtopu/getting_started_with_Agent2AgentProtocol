"""Repository-wide content, solution and offline assertions."""

import json

import nbformat
import pytest

from common.config import ROOT
from gym.engine import catalog, grade


@pytest.mark.parametrize("task", catalog(), ids=lambda task: task["id"])
def test_gym_solution(task):
    grade(task["path"], task["path"] / "solution")


@pytest.mark.parametrize("task", catalog(), ids=lambda task: task["id"])
def test_gym_starter_fails(task):
    with pytest.raises((AssertionError, ValueError, KeyError, TypeError)):
        grade(task["path"], task["path"] / "starter")


def test_notebooks_cleared():
    for path in (ROOT / "modules").rglob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                assert not cell.outputs, path
                assert cell.execution_count is None, path


def test_module_sections():
    sections = [
        "Prerequisites",
        "Learning objectives",
        "The big idea",
        "How it works",
        "On the wire",
        "Key APIs at a glance",
        "Walkthrough",
        "Try it in the Inspector and the Control Room",
        "Real-world use case",
        "Common bugs",
        "Practice",
        "Quiz",
        "Key takeaways",
        "Go deeper",
        "Next:",
    ]
    for module in json.loads((ROOT / "common/course_catalog.json").read_text()):
        matches = list((ROOT / "modules").rglob(f"{module['id']}_{module['slug']}/README.md"))
        assert len(matches) == 1
        text = matches[0].read_text(encoding="utf-8")
        assert all("## " + section in text for section in sections), matches[0]
        assert "Predict, then run" in text


def test_no_legacy_patterns():
    banned = [
        "/.well-known/" + "agent.json",
        "A2A" + "StarletteApplication",
        "A2A" + "FastAPIApplication",
        "supportsAuthenticated" + "ExtendedCard",
        '"method": "message' + '/send"',
        "from a2a.types import " + "TextPart",
    ]
    for directory in ["agents", "common", "modules", "gym", "scripts", "docs"]:
        for path in (ROOT / directory).rglob("*"):
            if (
                path.suffix not in {".py", ".md", ".json"}
                or "research" in path.parts
                or path.name == "MIGRATING_FROM_V0.md"
            ):
                continue
            text = path.read_text(encoding="utf-8")
            assert not any(pattern in text for pattern in banned), path


def test_no_provider_imports_in_tier_one():
    for module in range(9):
        for path in (ROOT / "modules").glob(f"{module:02}_*/examples/*.py"):
            text = path.read_text()
            assert all(
                name not in text for name in ["common.llm", "import openai", "import anthropic"]
            )
