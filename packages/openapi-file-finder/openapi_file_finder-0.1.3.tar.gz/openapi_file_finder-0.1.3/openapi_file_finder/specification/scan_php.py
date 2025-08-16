from __future__ import annotations

import os

from .async_utils import _file_contains_any_pattern_async
from .patterns import APIBLUEPRINT_PATTERNS
from .patterns import SWAGGER_PHP_PATTERNS
from openapi_file_finder.filesystem import enumerate_php_files


def _read_file(path: str, mode: str = 'r') -> bytes:
    try:
        with open(path, mode) as f:
            return f.read()
    except Exception:
        return b''


def _file_contains_any_pattern(path: str, patterns: list[bytes]) -> bool:
    if not os.path.isfile(path):
        return False
    content = _read_file(path, mode='rb')
    if content is None:
        return False
    return any(p in content for p in patterns)


def _check_repository_pattern_usage(repository_path: str, patterns: list[bytes]) -> bool:
    for php_file in enumerate_php_files(repository_path):
        if _file_contains_any_pattern(php_file, patterns):
            return True
    return False


async def _check_repository_pattern_usage_async(repository_path: str, patterns: list[bytes]) -> bool:
    files = list(enumerate_php_files(repository_path))
    import asyncio
    results = await asyncio.gather(*(_file_contains_any_pattern_async(f, patterns) for f in files))
    return any(results)


def check_repository_swagger_php_usage(repository_path: str) -> bool:
    """
    Return True if any PHP file in the repo uses swagger-php annotations.
    """
    return _check_repository_pattern_usage(repository_path, SWAGGER_PHP_PATTERNS)


async def check_repository_swagger_php_usage_async(repository_path: str) -> bool:
    """
    Async version of check_repository_swagger_php_usage.
    """
    return await _check_repository_pattern_usage_async(repository_path, SWAGGER_PHP_PATTERNS)


def check_repository_apiblueprint_usage(repository_path: str) -> bool:
    """
    Return True if any PHP file in the repo uses API Blueprint annotations.
    """
    return _check_repository_pattern_usage(repository_path, APIBLUEPRINT_PATTERNS)


async def check_repository_apiblueprint_usage_async(repository_path: str) -> bool:
    """
    Async version of check_repository_apiblueprint_usage.
    """
    return await _check_repository_pattern_usage_async(repository_path, APIBLUEPRINT_PATTERNS)
