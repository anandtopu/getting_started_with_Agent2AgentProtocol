"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return {"raw": payload["text"], "mediaType": payload["media_type"]}


def main() -> None:
    sample = json.loads(
        '{"text": "floor plan", "media_type": "text/plain", "filename": "plan.txt"}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
