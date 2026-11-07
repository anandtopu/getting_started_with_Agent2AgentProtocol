"""Validate task completeness, failing starters and passing reference solutions."""

from collections import defaultdict

from gym.engine import catalog, grade


def main() -> None:
    groups = defaultdict(list)
    tasks = catalog()
    assert len(tasks) >= 150, f"Expected 150 core and bonus tasks, found {len(tasks)}"
    for task in tasks:
        folder = task["path"]
        groups[task["module"]].append(task)
        for name in ["task.md", "task.json", "test_task.py", "hints.md", "explanation.md"]:
            assert (folder / name).is_file(), f"{task['id']}: missing {name}"
        assert (folder / "hints.md").read_text(encoding="utf-8").count("## Hint ") == 3
        grade(folder, folder / "solution")
        try:
            grade(folder, folder / "starter")
        except (AssertionError, ValueError, KeyError, TypeError):
            pass
        else:
            raise AssertionError(f"{task['id']}: starter unexpectedly passes")
    for module, items in groups.items():
        assert len(items) >= 6, module
        assert len({t["type"] for t in items}) >= 4, module
        assert {"easy", "medium", "hard"} <= {t["level"] for t in items}, module
    print(
        f"Validated {len(tasks)} tasks in {len(groups)} modules: every starter fails; every solution passes."
    )
    print("Design checks assess structure only; human rubric review remains required.")


if __name__ == "__main__":
    main()
