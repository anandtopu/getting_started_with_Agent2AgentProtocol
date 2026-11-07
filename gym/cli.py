"""Cross-platform Practice Gym. All graded work runs locally without API keys."""

import json
import os
import random
import shutil
import subprocess
import sys

import typer
from rich.console import Console
from rich.table import Table

from common.config import ROOT
from gym.engine import catalog, find

app = typer.Typer(no_args_is_help=True)
console = Console()
WORKSPACE = ROOT / "workspace"
PROGRESS = WORKSPACE / ".progress.json"


def progress_data() -> dict:
    return json.loads(PROGRESS.read_text(encoding="utf-8")) if PROGRESS.exists() else {}


def save_progress(data: dict) -> None:
    WORKSPACE.mkdir(exist_ok=True)
    temp = PROGRESS.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, PROGRESS)


def get_task(task_id: str):
    try:
        return find(task_id)
    except ValueError as exc:
        console.print(str(exc))
        raise typer.Exit(2) from None


@app.command("list")
def list_tasks(module: str = "", type: str = "", level: str = "") -> None:
    table = Table("ID", "Module", "Type", "Level", "Task")
    for task in catalog():
        if (
            (not module or task["module"] == module)
            and (not type or task["type"] == type)
            and (not level or task["level"] == level)
        ):
            table.add_row(task["id"], task["module"], task["type"], task["level"], task["title"])
    console.print(table)


@app.command()
def start(task_id: str) -> None:
    task = get_task(task_id)
    destination = WORKSPACE / task_id
    if destination.exists():
        console.print(f"Attempt already exists: {destination}. Use gym reset to start over.")
        raise typer.Exit(1)
    shutil.copytree(task["path"] / "starter", destination)
    console.print((task["path"] / "task.md").read_text(encoding="utf-8"))
    console.print(f"Edit {destination}; then run gym check {task_id}.")


@app.command()
def check(task_id: str) -> None:
    task = get_task(task_id)
    attempt = WORKSPACE / task_id
    if not attempt.exists():
        console.print(f"Run gym start {task_id} first.")
        raise typer.Exit(1)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(task["path"] / "test_task.py"), "-q", "--tb=short"],
        cwd=ROOT,
        env={**os.environ, "GYM_ATTEMPT": str(attempt)},
        timeout=60,
    )
    data = progress_data()
    entry = data.setdefault(task_id, {})
    entry["attempts"] = entry.get("attempts", 0) + 1
    if result.returncode == 0:
        entry["passed"] = True
        entry["review_required"] = task["type"] == "design"
        console.print(
            "Structure passed; complete the human rubric before claiming design proficiency."
            if entry["review_required"]
            else "Passed. Read explanation.md, then try gym next."
        )
    save_progress(data)
    raise typer.Exit(result.returncode)


@app.command()
def hint(task_id: str) -> None:
    task = get_task(task_id)
    hints = (task["path"] / "hints.md").read_text(encoding="utf-8").split("## Hint ")[1:]
    data = progress_data()
    entry = data.setdefault(task_id, {})
    index = min(entry.get("hints", 0), 2)
    console.print(hints[index])
    entry["hints"] = min(index + 1, 3)
    save_progress(data)


@app.command()
def solution(task_id: str, yes: bool = typer.Option(False, "--yes")) -> None:
    task = get_task(task_id)
    if not yes and not typer.confirm("Reveal the reference solution and mark it viewed?"):
        raise typer.Exit()
    for path in sorted((task["path"] / "solution").iterdir()):
        if path.is_file():
            console.print(path.read_text(encoding="utf-8"), markup=False)
    console.print((task["path"] / "explanation.md").read_text(encoding="utf-8"))
    data = progress_data()
    data.setdefault(task_id, {})["solution_viewed"] = True
    save_progress(data)


@app.command()
def reset(task_id: str, yes: bool = typer.Option(False, "--yes")) -> None:
    task = get_task(task_id)
    destination = (WORKSPACE / task_id).resolve()
    if destination.parent != WORKSPACE.resolve():
        raise typer.Exit(2)
    if not yes and not typer.confirm(
        f"Replace your attempt for {task_id}? Progress and hints will reset."
    ):
        raise typer.Exit()
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(task["path"] / "starter", destination)
    data = progress_data()
    data.pop(task_id, None)
    save_progress(data)


@app.command()
def progress() -> None:
    data = progress_data()
    for key in ("module", "type"):
        groups = sorted({task[key] for task in catalog()})
        for group in groups:
            tasks = [task for task in catalog() if task[key] == group]
            done = sum(bool(data.get(task["id"], {}).get("passed")) for task in tasks)
            console.print(f"{key} {group}: {done}/{len(tasks)} checks passed")


@app.command("next")
def next_task() -> None:
    data = progress_data()
    task = next((task for task in catalog() if not data.get(task["id"], {}).get("passed")), None)
    console.print(
        f"Next: gym start {task['id']} — {task['title']}"
        if task
        else "All checks passed. Review design rubrics and try a capstone."
    )


@app.command()
def drill(seed: int | None = None) -> None:
    data = progress_data()
    all_tasks = catalog()
    finished = {
        t["module"]
        for t in all_tasks
        if all(data.get(x["id"], {}).get("passed") for x in all_tasks if x["module"] == t["module"])
    }
    choices = [
        t for t in all_tasks if t["module"] in finished and t["type"] in {"predict", "trace"}
    ]
    if not choices:
        console.print("Finish one module's checks first; gym next recommends your next task.")
        return
    for task in random.Random(seed).sample(choices, min(5, len(choices))):
        console.print(f"Review {task['id']}: {task['title']}")


if __name__ == "__main__":
    app()
