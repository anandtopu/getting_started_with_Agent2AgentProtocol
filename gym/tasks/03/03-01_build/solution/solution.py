"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return ["task", "working"] + payload["artifacts"] + ["completed"]


def main() -> None:
    sample = json.loads('{"artifacts": ["quote"]}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
