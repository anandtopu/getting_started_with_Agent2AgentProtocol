"""Initialize the pinned schema before starting replicas; credentials come from environment."""

import argparse
import asyncio
import os

from sqlalchemy.ext.asyncio import create_async_engine

from agents.catalog import card
from common.cluster import ClusterStore
from common.config import PORTS, Settings
from common.key_rotation import SharedCardKeys
from common.reservations import ReservationStore
from common.security import unb64


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor", choices=PORTS, required=True)
    args = parser.parse_args()
    database = Settings().database_url
    if not database:
        parser.error("Set DATABASE_URL in the deployment environment.")
    engine = create_async_engine(database)
    try:
        await ClusterStore(engine, args.vendor).initialize()
        if args.vendor in {"venues", "travel"}:
            await ReservationStore(engine, args.vendor).initialize()
        if os.environ.get("MAPLEWOOD_HARDENED") == "1":
            key = unb64(os.environ["MAPLEWOOD_SIGNING_KEY"])
            await SharedCardKeys(card(args.vendor), engine, args.vendor, key).initialize()
        print(f"{args.vendor}: pinned database schema initialized.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
