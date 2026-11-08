# Why this works

A persisted event and its configured delivery must both be visible after one commit.

The exercise uses real persistence objects and protocol state. A task version, identity or signing key is evidence with a precise scope; treating one as another creates silent cross-tenant or recovery bugs. The implementation is bounded and has no external dependencies at grading time.

~~~python
async def exercise(context):
    from sqlalchemy import select, func

    store = context["two"]
    async with store.engine.connect() as connection:
        return [
            (await connection.execute(select(func.count()).select_from(table))).scalar_one()
            for table in (store.events, store.outbox)
        ]
~~~
