"""Transform one Maplewood input according to task.md; no services or model needed."""

import json


def solve(payload: object) -> object:
    # YOUR CODE HERE: preserve the function interface used by the grader.
    return next(
        (
            i["url"]
            for i in payload["interfaces"]
            if i["protocolBinding"] in payload["supported"] and i["protocolVersion"] == "1.0"
        ),
        None,
    )


def main() -> None:
    sample = json.loads(
        '{"interfaces": [{"url": "http://print", "protocolBinding": "GRPC", "protocolVersion": "1.0"}, {"url": "http://venues", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}], "supported": ["JSONRPC"]}'
    )
    print(json.dumps(solve(sample), indent=2))


if __name__ == "__main__":
    main()
