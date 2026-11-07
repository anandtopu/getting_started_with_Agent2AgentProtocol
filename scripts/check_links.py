"""Check local Markdown links; --online additionally verifies external HTTP links."""

import argparse
import concurrent.futures
import re
from urllib.parse import unquote, urlsplit

import httpx

from common.config import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    external, failures, checked = set(), [], 0
    ignored = {".venv", ".git", "node_modules", "workspace", "research"}
    for path in ROOT.rglob("*.md"):
        if ignored.intersection(path.relative_to(ROOT).parts):
            continue
        for target in re.findall(
            r"\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", path.read_text(encoding="utf-8")
        ):
            if target.startswith(("http://", "https://")):
                external.add(target)
                continue
            if target.startswith(("#", "mailto:")):
                continue
            local = unquote(urlsplit(target.strip("<>")).path)
            if local:
                checked += 1
                if not (path.parent / local).exists():
                    failures.append(f"{path.relative_to(ROOT)} -> {target}")
    if args.online:

        def verify(url):
            try:
                result = httpx.get(
                    url,
                    follow_redirects=True,
                    timeout=20,
                    headers={"User-Agent": "Maplewood-course-link-check/0.1"},
                )
                return None if result.status_code < 400 else f"{url}: HTTP {result.status_code}"
            except httpx.HTTPError as exc:
                return f"{url}: {type(exc).__name__}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            failures += [failure for failure in pool.map(verify, external) if failure]
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print(
        f"Checked {checked} local links. External URLs: {len(external)} ({'checked' if args.online else 'not requested'})."
    )


if __name__ == "__main__":
    main()
