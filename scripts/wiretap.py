"""Capture offline lessons or run an explicit local logging proxy."""

import argparse
import asyncio
import json
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import Response

from common.lessons import experiment
from common.wire import Recorder


async def capture(name: str, output: Path) -> None:
    records = []
    result = await experiment(name, records)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(item) + "\n" for item in records), encoding="utf-8")
    print(json.dumps(result, indent=2))


def proxy(upstream: str, output: Path):
    if not upstream.startswith("http://127.0.0.1:"):
        raise ValueError("The teaching proxy accepts an explicit loopback upstream only.")
    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "DELETE"])
    async def forward(path: str, request: Request):
        recorder = Recorder(httpx.AsyncHTTPTransport())
        async with httpx.AsyncClient(transport=recorder, timeout=30) as http:
            headers = {
                key: value
                for key, value in request.headers.items()
                if key.lower() not in {"host", "content-length", "connection"}
            }
            response = await http.request(
                request.method,
                upstream.rstrip("/") + "/" + path,
                params=request.query_params,
                headers=headers,
                content=await request.body(),
            )
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("a", encoding="utf-8") as handle:
                for record in recorder.records:
                    handle.write(json.dumps(record) + "\n")
            return Response(
                response.content,
                status_code=response.status_code,
                media_type=response.headers.get("content-type"),
            )

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", default="jsonrpc")
    parser.add_argument("--output", type=Path, default=Path("workspace/wire.jsonl"))
    parser.add_argument(
        "--upstream", help="Optional HTTP loopback proxy; buffers streams for inspection"
    )
    args = parser.parse_args()
    if args.upstream:
        uvicorn.run(proxy(args.upstream, args.output), host="127.0.0.1", port=8099)
    else:
        asyncio.run(capture(args.lesson, args.output))


if __name__ == "__main__":
    main()
