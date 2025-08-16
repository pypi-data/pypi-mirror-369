from __future__ import annotations

import os
from typing import Literal

import aiofiles


async def _read_file_async(path: str, mode: Literal['r', 'rb', 'w', 'wb', 'a', 'ab'] = 'rb') -> bytes:
    """
    Asynchronously read the contents of a file.
    """
    try:
        async with aiofiles.open(path, mode) as f:
            content = await f.read()
            return content.encode('utf-8') if isinstance(content, str) else content
    except OSError:
        return b''


async def _file_contains_any_pattern_async(path: str, patterns: list[bytes]) -> bool:
    """
    Asynchronously check if a file contains any of the given byte patterns.
    """
    if not os.path.isfile(path):
        return False
    content = await _read_file_async(path)
    if not content:
        return False
    return any(p in content for p in patterns)
