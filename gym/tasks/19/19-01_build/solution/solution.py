"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return (
        min(payload["base_seconds"] * 2 ** payload["attempt"], payload["cap_seconds"])
        if payload["attempt"] < payload["max_attempts"]
        else None
    )


def main() -> None:
    sample = json.loads('{"base_seconds": 1, "attempt": 2, "cap_seconds": 3, "max_attempts": 5}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
