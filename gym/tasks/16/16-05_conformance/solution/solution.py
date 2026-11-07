"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    if not payload:
        return False
    if payload[0] == "message":
        return len(payload) == 1
    return (
        payload[0] == "task"
        and "message" not in payload
        and payload[-1]
        in {"completed", "failed", "canceled", "rejected", "input-required", "auth-required"}
    )


def main() -> None:
    sample = json.loads('["message"]')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
