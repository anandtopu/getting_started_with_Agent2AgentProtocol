"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return (
        ["release:" + hold["id"] for hold in reversed(payload["holds"]) if hold["confirmed"]]
        if payload["failed"]
        else []
    )


def main() -> None:
    sample = json.loads(
        '{"failed": true, "holds": [{"id": "hotel", "confirmed": true}, {"id": "venue", "confirmed": false}]}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
