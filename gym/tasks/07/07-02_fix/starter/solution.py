"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return {chunk["id"]: chunk["text"] for chunk in payload}


def main() -> None:
    sample = json.loads(
        '[{"id": "a", "text": "Mic "}, {"id": "b", "text": "Light"}, {"id": "a", "text": "check", "append": true}]'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
