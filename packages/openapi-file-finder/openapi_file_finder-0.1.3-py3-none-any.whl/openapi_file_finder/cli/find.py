from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from .utils import run_async
from openapi_file_finder.specification import find_and_validate_openapi_file
from openapi_file_finder.specification import find_and_validate_openapi_file_async
from openapi_file_finder.specification import find_and_validate_openapi_files
from openapi_file_finder.specification import find_and_validate_openapi_files_async

console = Console()


def find(
    repo_path: str = typer.Argument(
        ...,
        help='Path to the repository to scan',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation for better performance on large repos.',
    ),
):
    """
    Find and validate OpenAPI/Swagger specification files in the repository.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        files = run_async(find_and_validate_openapi_files_async(repo_path))
    else:
        files = find_and_validate_openapi_files(repo_path)
    if files:
        table = Table(title='OpenAPI/Swagger Specification Files')
        table.add_column('File Path', style='cyan')
        for f in files:
            table.add_row(f)
        console.print(table)
        logger.info('found_openapi_files', count=len(files))
    else:
        console.print(
            '[bold red]No valid OpenAPI/Swagger specification files found.[/bold red]',
        )
        logger.warning('no_openapi_files_found')


def largest(
    file_path: str = typer.Argument(
        ..., help='Specify a file path to find the largest OpenAPI file in the same directory',
    ),
    use_async: bool = typer.Option(
        False, '--async', help='Use async implementation.',
    ),
):
    """
    Find the largest OpenAPI file in the same directory as the specified file.
    """
    import structlog
    logger = structlog.get_logger()
    if use_async:
        result = run_async(find_and_validate_openapi_file_async(file_path))
    else:
        result = find_and_validate_openapi_file(file_path)
    if result:
        console.print(
            f"[bold green]Largest OpenAPI file found: {result}[/bold green]",
        )
        logger.info('max_openapi_file_found', file=result)
    else:
        console.print('[bold red]No valid OpenAPI file found.[/bold red]')
        logger.warning('no_openapi_file_found')
