"""All graded tests are offline; Windows only needs its event-loop wakeup socket."""

import asyncio
import socket
import sys

import pytest
import pytest_socket


def offline_loop():
    saved = socket.socket, socket.getaddrinfo, socket.gethostbyname
    try:
        # Only construct asyncio's internal wakeup pair; no learner code runs here.
        pytest_socket.enable_socket()
        return asyncio.ProactorEventLoop() if sys.platform == "win32" else asyncio.new_event_loop()
    finally:
        socket.socket, socket.getaddrinfo, socket.gethostbyname = saved


def pytest_asyncio_loop_factories():
    return {"offline": offline_loop}


def pytest_collection_modifyitems(config, items):
    explicit = config.getoption("markexpr")
    for item in items:
        for marker in ("docker", "live"):
            if marker in item.keywords and marker not in explicit:
                item.add_marker(pytest.mark.skip(reason=f"Use -m {marker} to opt in."))
