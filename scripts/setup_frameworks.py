"""Install independent locked framework environments; initial setup requires internet."""

import argparse
import shutil
import subprocess

from common.config import ROOT
from common.frameworks import FRAMEWORKS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", choices=FRAMEWORKS)
    args = parser.parse_args()
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("Install uv, then rerun this command.")
    for name in [args.framework] if args.framework else FRAMEWORKS:
        subprocess.run(
            [uv, "sync", "--project", str(ROOT / "integrations" / name), "--locked"], check=True
        )
    print("Framework environments are ready. Run scripts/check_frameworks.py.")


if __name__ == "__main__":
    main()
