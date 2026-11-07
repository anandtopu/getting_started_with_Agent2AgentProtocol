"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    routes = {
        "SendMessage": ("POST", "/message:send"),
        "GetTask": ("GET", "/tasks/" + payload.get("id", "")),
        "CancelTask": ("POST", "/tasks/" + payload.get("id", "") + ":cancel"),
    }
    return list(routes[payload["operation"]])


def main() -> None:
    sample = json.loads('{"operation": "SendMessage"}')
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
