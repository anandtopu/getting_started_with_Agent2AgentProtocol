"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return sum(key in payload for key in ("text", "raw", "url", "data")) == 1


def main() -> None:
    sample = json.loads('{"text": "quote"}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
