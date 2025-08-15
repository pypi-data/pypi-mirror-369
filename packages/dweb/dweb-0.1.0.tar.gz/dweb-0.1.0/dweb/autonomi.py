from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union

from autonomi_client import DataAddress

from . import network as network_mod
from importlib import import_module


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="dweb-autonomi")


def _run_coro_in_thread(coro):
    def _runner():
        return asyncio.run(coro)

    return _executor.submit(_runner).result()


def get(
    address: Union[str, DataAddress],
    *,
    network: network_mod._Network = network_mod.mainnet,
    timeout: Optional[float] = None,
) -> bytes:
    """Synchronous wrapper around the async `get` API.

    Args:
        address: 64-hex data map address (string) or `DataAddress`.
        network: network selector (`network.mainnet` or `network.alpha`).
        timeout: optional timeout in seconds for the operation.
    """

    # Lazy import to allow monkeypatching in tests and avoid import cycles during startup
    async_api = import_module("dweb.aio.autonomi")
    coro = async_api.get(address, network=network)

    # If already in an event loop (e.g., Jupyter), we must not nest loops.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        future = _executor.submit(lambda: asyncio.run(coro))
        return future.result(timeout=timeout)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout) if timeout else coro)


