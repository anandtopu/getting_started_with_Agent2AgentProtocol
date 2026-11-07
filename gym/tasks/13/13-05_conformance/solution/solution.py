"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return payload["authenticated"] and (
        payload["skill"] != "travel.partner_quote" or "partner" in payload["scopes"]
    )


def main() -> None:
    sample = json.loads('{"authenticated": true, "skill": "travel.partner_quote", "scopes": []}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
