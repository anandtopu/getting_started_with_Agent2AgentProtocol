"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    import base64

    return {
        "raw": base64.b64encode(payload["text"].encode()).decode(),
        "mediaType": payload["media_type"],
        "filename": payload["filename"],
    }


def main() -> None:
    sample = json.loads(
        '{"text": "floor plan", "media_type": "text/plain", "filename": "plan.txt"}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
