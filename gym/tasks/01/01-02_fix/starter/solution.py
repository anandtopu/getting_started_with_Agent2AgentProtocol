"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return {
        "jsonrpc": "2.0",
        "id": payload["id"],
        "method": "SendMessage",
        "params": payload["message"],
    }


def main() -> None:
    sample = json.loads(
        '{"id": 1, "message": {"messageId": "m1", "role": "ROLE_USER", "parts": [{"text": "Quote a venue"}]}}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
