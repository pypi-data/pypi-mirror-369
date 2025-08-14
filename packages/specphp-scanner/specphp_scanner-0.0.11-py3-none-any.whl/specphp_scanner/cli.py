"""Command-line interface module for OpenAPI Scanner.

This module provides the command-line interface for scanning APIs based on OpenAPI specifications.
It handles file loading, authentication, and coordinates the scanning process.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog
import typer
import yaml
from rich.console import Console

from specphp_scanner.auth.factory import AuthFactory
from specphp_scanner.core.scanner import scan_api
from specphp_scanner.utils.request_logger import RequestLogger

logger = structlog.get_logger()

console = Console()
app = typer.Typer()


def load_spec_file(file_path: Path) -> dict[str, Any]:
    """Load OpenAPI specification from JSON or YAML file.

    Args:
        file_path: Path to the specification file

    Returns:
        Dict containing the OpenAPI specification

    Raises:
        FileNotFoundError: If the specification file does not exist
        ValueError: If the file format is not supported or the file is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Specification file not found: {file_path}")

    try:
        with open(file_path) as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}",
                )
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid specification file: {e}")


@app.command()
def main(
    spec_file: str = typer.Argument(
        ...,
        help='Path to the PHP project directory to analyze',
    ),
    host: str = typer.Option(
        ...,
        '--host',
        '-h',
        help='Target host',
    ),
    port: int = typer.Option(
        ...,
        '--port',
        '-p',
        help='Target port',
    ),
    auth_class: str | None = typer.Option(
        None,
        '--auth-class',
        '-a',
        help="Full path to the authentication class (e.g. 'examples.koel.auth.KoelAuth')",
    ),
    no_replace_params: bool = typer.Option(
        False,
        '--no-replace-params',
        help='Disable path parameter replacement',
    ),
    auth_params: str | None = typer.Option(
        None,
        '--auth-params',
        help='JSON string containing authentication parameters',
    ),
    headers: str | None = typer.Option(
        None,
        '--headers',
        help='JSON string containing custom headers to include in all requests',
    ),
    verbose: bool = typer.Option(
        False,
        '--verbose',
        '-v',
        help='Enable verbose logging',
    ),
    disable_request_logging: bool = typer.Option(
        False,
        '--disable-request-logging',
        help='Disable request logging to stderr (enabled by default)',
    ),
    request_log_file: Path | None = typer.Option(
        None,
        '--request-log-file',
        help='Path to save request logs in JSONL format (optional)',
    ),
) -> None:
    """Run the API scanner with configurable path parameter replacement.

    Args:
        spec_file: Path to the OpenAPI specification file
        auth_class: Path to the authentication class
        host: Target host
        port: Target port
        no_replace_params: Whether to disable path parameter replacement
        auth_params: JSON string containing authentication parameters
        headers: JSON string containing custom headers
        verbose: Whether to enable verbose logging
        disable_request_logging: Whether to disable request logging to stderr
        request_log_file: Path to save request logs in JSONL format (optional)
    """
    # Validate spec_file parameter
    if not spec_file:
        raise typer.Exit()

    spec_file_path = Path(spec_file)

    # Load OpenAPI spec
    try:
        data = load_spec_file(spec_file_path)
        logger.info('OpenAPI specification loaded', file=str(spec_file_path))
    except (FileNotFoundError, ValueError) as e:
        logger.error(
            'Failed to load OpenAPI specification',
            file=str(spec_file_path), error=str(e),
        )
        raise typer.BadParameter(str(e))

    # Initialize auth instance
    auth = None
    if auth_class:
        # Parse auth parameters
        auth_kwargs: dict[str, Any] = {}
        if auth_params:
            try:
                auth_kwargs = json.loads(auth_params)
                logger.debug('Auth parameters parsed', params=auth_kwargs)
            except json.JSONDecodeError:
                logger.error(
                    'Invalid JSON in auth-params',
                    auth_params=auth_params,
                )
                raise typer.BadParameter('Invalid JSON in auth-params')

        # Create auth instance
        try:
            auth = AuthFactory.create(auth_class, **auth_kwargs)
            logger.info(
                'Authentication instance created',
                auth_class=auth_class,
            )
        except ValueError as e:
            logger.error(
                'Failed to create auth instance',
                auth_class=auth_class, error=str(e),
            )
            raise typer.BadParameter(str(e))

    # Get headers and cookies
    headers_dict: dict[str, str] = {}
    cookies: dict[str, str] = {}

    # Add custom headers if specified
    if headers:
        try:
            headers_dict.update(json.loads(headers))
            logger.debug('Custom headers added', headers=headers_dict)
        except json.JSONDecodeError:
            logger.error('Invalid JSON in headers', headers=headers)
            raise typer.BadParameter('Invalid JSON in headers')

    # Add auth headers if authentication is enabled
    if auth:
        try:
            base_url = f"http://{host}:{port}"
            headers_dict.update(auth.get_headers(base_url))
            cookies = auth.get_cookies(base_url)
            logger.info(
                'Authentication headers and cookies added',
                base_url=base_url,
            )
        except Exception as e:
            logger.error(
                'Authentication failed',
                base_url=base_url, error=str(e),
            )
            console.print(f"[red]Authentication failed: {str(e)}[/red]")
            raise typer.Exit(1)

    # Initialize request logger (enabled by default)
    request_logger = None
    if not disable_request_logging:
        # Enable console output by default, optionally save to file
        console_output = True
        if request_log_file:
            request_logger = RequestLogger(
                log_file=request_log_file,
                console_output=console_output,
            )
            logger.info(
                'Request logging enabled',
                log_file=str(request_log_file),
            )
            console.print(
                f"[blue]Request logging enabled. Logs will be saved to: {request_log_file}[/blue]",
            )
        else:
            request_logger = RequestLogger(
                log_file=None,
                console_output=console_output,
            )
            logger.info('Request logging enabled (console output only)')
            console.print(
                '[blue]Request logging enabled (output to stderr)[/blue]',
            )

    # Run the scanner
    try:
        logger.info('Starting API scan', host=host, port=port)
        results = scan_api(
            host=host,
            port=port,
            headers=headers_dict,
            cookies=cookies,
            data=data,
            replace_params=not no_replace_params,
            request_logger=request_logger,
        )

        if not results:
            logger.warning('No API endpoints found in the specification')
            console.print(
                '[yellow]No API endpoints found in the specification[/yellow]',
            )
            return

        logger.info('API scan completed', results_count=len(results))

        # Display request logging statistics if enabled
        if request_logger:
            stats = request_logger.get_stats()
            logger.info('Request logging statistics', stats=stats)
            console.print('\n[blue]Request Logging Statistics:[/blue]')
            console.print(f"  Total requests: {stats['total_requests']}")
            console.print(f"  Total responses: {stats['total_responses']}")
            console.print(f"  Total errors: {stats['total_errors']}")
            if stats['log_file']:
                console.print(f"  Log file: {stats['log_file']}")
            else:
                console.print('  Log file: None (console output only)')

            if stats['method_distribution']:
                console.print(
                    f"  Method distribution: {stats['method_distribution']}",
                )
            if stats['status_code_distribution']:
                console.print(
                    f"  Status code distribution: {stats['status_code_distribution']}",
                )

        # Print results to console
        for result in results:
            if result.status_code is not None:
                status_color = '\033[92m' if 200 <= result.status_code < 300 else '\033[91m'
                console.print(
                    f"{status_color}{result.method} {result.url} - {result.status_code}\033[0m",
                )
            else:
                console.print(
                    f"\033[91m{result.method} {result.url} - ERROR\033[0m",
                )
            if result.error:
                console.print(f"Error: {result.error}")
            if result.response:
                console.print(f"Response: {result.response}")
            console.print()

    except Exception as e:
        logger.error('Scan failed', error=str(e))
        console.print(f"[red]Scan failed: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == '__main__':
    app()
