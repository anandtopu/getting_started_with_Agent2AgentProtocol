"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return not payload["address"].startswith("127.")


def main() -> None:
    sample = json.loads('{"address": "127.0.0.1"}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
