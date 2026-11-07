"""Run one local vendor: uv run maplewood --vendor venues --demo."""

import argparse
import json
import os

import uvicorn
from a2a.server.tasks import DatabaseTaskStore
from sqlalchemy.ext.asyncio import create_async_engine

from agents.app import make_app, make_handler
from agents.concierge_executor import ConciergeExecutor
from common.config import PORTS, Settings
from common.observability import configure_tracing
from common.security import Principal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor", choices=PORTS, default="venues")
    parser.add_argument(
        "--demo", action="store_true", help="No authentication, earliest lessons only"
    )
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    settings = Settings()
    if args.demo and args.host != "127.0.0.1":
        parser.error("Unauthenticated demos must listen only on 127.0.0.1.")
    if not args.demo and not settings.maplewood_token:
        parser.error(
            "Missing MAPLEWOOD_TOKEN. Use uv run python scripts/network.py up --module 07."
        )
    tracing = configure_tracing()
    engine = create_async_engine(settings.database_url) if settings.database_url else None
    store = DatabaseTaskStore(engine, table_name=args.vendor + "_tasks") if engine else None
    handler = make_handler(args.vendor, secure=not args.demo, task_store=store)
    if args.vendor == "print":
        from agents.grpc_server import run

        run(settings.maplewood_token, args.host, handler=handler, engine=engine)
        return
    if args.vendor == "concierge":
        tokens = json.loads(os.environ.get("MAPLEWOOD_VENDOR_TOKENS", "{}"))
        handler = make_handler(
            "concierge", secure=not args.demo, executor=ConciergeExecutor(tokens), task_store=store
        )
    app = make_app(
        args.vendor,
        demo=args.demo,
        tokens={settings.maplewood_token: Principal("concierge")},
        handler=handler,
        engine=engine,
    )
    uvicorn.run(app, host=args.host, port=PORTS[args.vendor], log_level="info")
    if tracing:
        tracing.shutdown()


if __name__ == "__main__":
    main()
