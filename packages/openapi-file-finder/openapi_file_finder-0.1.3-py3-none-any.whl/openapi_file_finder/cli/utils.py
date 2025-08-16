from __future__ import annotations

import asyncio


def run_async(coro):
    """Run an async coroutine in a synchronous context."""
    return asyncio.run(coro)
