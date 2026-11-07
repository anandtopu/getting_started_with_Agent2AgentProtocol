"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return [release["language"] for release in payload]


def main() -> None:
    sample = json.loads(
        '[{"language": "Go", "protocols": ["1.0"], "stable": true}, {"language": "Java", "protocols": ["0.3"], "stable": true}]'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
