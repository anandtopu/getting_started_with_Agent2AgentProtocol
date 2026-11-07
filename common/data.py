"""Load committed synthetic data without depending on the working directory."""

import json
from typing import Any

from common.config import ROOT


def load(name: str) -> Any:
    path = (ROOT / "data" / name).resolve()
    if not path.is_relative_to(ROOT / "data"):
        raise ValueError("Data path must remain inside data/.")
    return json.loads(path.read_text(encoding="utf-8"))
