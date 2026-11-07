"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return {
        "vendor": payload["vendor"],
        "total_cents": int(payload["amount"]),
        "currency": "USD",
        "approved": False,
    }


def main() -> None:
    sample = json.loads('{"vendor": "catering", "amount": "96000"}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
