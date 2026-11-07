"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return payload["task"]["tenant"] == payload["principal"]["tenant"]


def main() -> None:
    sample = json.loads(
        '{"task": {"owner": "alice", "tenant": "maplewood"}, "principal": {"subject": "bob", "tenant": "maplewood"}}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
