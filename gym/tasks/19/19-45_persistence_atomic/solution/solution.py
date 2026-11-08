async def exercise(context):
    from sqlalchemy import func, select

    store = context["two"]
    async with store.engine.connect() as connection:
        return [
            (await connection.execute(select(func.count()).select_from(table))).scalar_one()
            for table in (store.events, store.outbox)
        ]
