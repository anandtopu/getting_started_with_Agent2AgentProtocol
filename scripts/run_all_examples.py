"""Execute every documented example as a standalone process, plus notebooks."""

import argparse
import subprocess
import sys

import nbformat

from common.config import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebooks", action="store_true")
    args = parser.parse_args()
    paths = sorted((ROOT / "modules").glob("**/examples/*.py"))
    paths += sorted((ROOT / "modules").glob("**/use_case/run.py"))
    for path in paths:
        result = subprocess.run(
            [sys.executable, str(path)], cwd=ROOT, capture_output=True, text=True, timeout=60
        )
        if result.returncode:
            print(result.stdout, result.stderr)
            raise SystemExit(f"Failed: {path.relative_to(ROOT)}")
    print(f"Passed {len(paths)} standalone example/use-case commands.")
    if args.notebooks:
        for path in (ROOT / "modules").rglob("notebook.ipynb"):
            notebook = nbformat.read(path, as_version=4)
            code = "\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
            wrapper = (
                "import asyncio\nasync def main():\n"
                + "\n".join("    " + line for line in code.splitlines())
                + "\nasyncio.run(main())"
            )
            result = subprocess.run(
                [sys.executable, "-c", wrapper],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode:
                print(result.stderr)
                raise SystemExit(f"Failed notebook: {path}")
        print("All notebook code cells executed top to bottom.")


if __name__ == "__main__":
    main()
