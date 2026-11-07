"""Close the database and handler, then resume with entirely new objects."""

from a2a.server.tasks import DatabaseTaskStore
from sqlalchemy.ext.asyncio import create_async_engine

from agents.app import make_handler
from common.protocol import as_dict, request
from common.testing import client


async def test_pause_survives_server_restart(tmp_path):
    database = "sqlite+aiosqlite:///" + (tmp_path / "tasks.db").as_posix()
    first_engine = create_async_engine(database)
    async with client(
        "catering", handler=make_handler("catering", task_store=DatabaseTaskStore(first_engine))
    ) as http:
        first = (await http.post("/message:send", json=as_dict(request({"guests": 40})))).json()[
            "task"
        ]
    await first_engine.dispose()
    second_engine = create_async_engine(database)
    try:
        async with client(
            "catering",
            handler=make_handler("catering", task_store=DatabaseTaskStore(second_engine)),
        ) as http:
            message = request(
                {"dietary": {"vegan": 40}}, task_id=first["id"], context_id=first["contextId"]
            )
            second = (await http.post("/message:send", json=as_dict(message))).json()["task"]
            assert second["id"] == first["id"]
            assert second["status"]["state"] == "TASK_STATE_COMPLETED"
    finally:
        await second_engine.dispose()
