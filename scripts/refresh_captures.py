"""Refresh real captures and prediction fixtures without overwriting authored lessons."""

import asyncio
import json

from common.config import ROOT
from common.lessons import experiment
from scripts.build_course import clean


async def main():
    modules = json.loads((ROOT / "common/course_catalog.json").read_text())
    for module in modules:
        folder = next((ROOT / "modules").rglob(f"{module['id']}_{module['slug']}"))
        for index, lab in enumerate(module["labs"], 1):
            records = []
            result = await experiment(lab, records)
            stem = folder / "wire" / f"{index:02}_{lab}"
            stem.with_suffix(".jsonl").write_text(
                "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8"
            )
            stem.with_suffix(".result.json").write_text(
                json.dumps(result, indent=2) + "\n", encoding="utf-8"
            )
            if index == 1:
                prediction = (
                    ROOT
                    / "gym/tasks"
                    / module["id"]
                    / f"{module['id']}-03_predict/solution/answer.json"
                )
                prediction.write_text(json.dumps(clean(result), indent=2) + "\n", encoding="utf-8")
    print("Refreshed every module capture and its first-example prediction.")


if __name__ == "__main__":
    asyncio.run(main())
