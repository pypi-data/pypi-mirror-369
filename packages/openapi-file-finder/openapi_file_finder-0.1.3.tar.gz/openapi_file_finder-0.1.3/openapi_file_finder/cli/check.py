from __future__ import annotations

import typer
from rich.console import Console

from .utils import run_async
from openapi_file_finder.specification import check_repository_apiblueprint_usage
from openapi_file_finder.specification import check_repository_apiblueprint_usage_async
from openapi_file_finder.specification import check_repository_swagger_php_usage
from openapi_file_finder.specification import check_repository_swagger_php_usage_async

console = Console()


def check_swagger_php(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the PHP repository to scan',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation.',
    ),
    log_level: str | None = typer.Option(
        'info', '--log-level', help='Set log level (debug, info, warning, error)',
    ),
):
    """
    Check if swagger-php annotations are used in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        result = run_async(check_repository_swagger_php_usage_async(repo_path))
    else:
        result = check_repository_swagger_php_usage(repo_path)
    if result:
        console.print(
            '[bold green]swagger-php annotations detected.[/bold green]',
        )
        logger.info('swagger_php_found')
    else:
        console.print(
            '[bold yellow]No swagger-php annotations detected.[/bold yellow]',
        )
        logger.info('swagger_php_not_found')


def check_apiblueprint(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the PHP repository to scan',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation.',
    ),
    log_level: str | None = typer.Option(
        'info', '--log-level', help='Set log level (debug, info, warning, error)',
    ),
):
    """
    Check if API Blueprint annotations are used in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        result = run_async(
            check_repository_apiblueprint_usage_async(repo_path),
        )
    else:
        result = check_repository_apiblueprint_usage(repo_path)
    if result:
        console.print(
            '[bold green]API Blueprint annotations detected.[/bold green]',
        )
        logger.info('apiblueprint_found')
    else:
        console.print(
            '[bold yellow]No API Blueprint annotations detected.[/bold yellow]',
        )
        logger.info('apiblueprint_not_found')
