"""Core scanning functionality for OpenAPI Scanner.

This module provides the main scanning logic for testing API endpoints defined in OpenAPI specifications.
It handles request generation, execution, and result collection.
"""
from __future__ import annotations

from typing import Any

import requests
import structlog
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from specphp_scanner.core.result import ScanResult
from specphp_scanner.utils.param_generator import generate_path_params
from specphp_scanner.utils.request_logger import RequestLogger

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

console = Console()


def scan_api(
    host: str,
    port: int,
    headers: dict[str, str],
    cookies: dict[str, str],
    data: dict[str, Any],
    replace_params: bool = True,
    request_logger: RequestLogger | None = None,
) -> list[ScanResult]:
    """Scan API endpoints defined in the OpenAPI specification.

    Args:
        host: Target host
        port: Target port
        headers: Request headers to include
        cookies: Cookies to include in requests
        data: OpenAPI specification data
        replace_params: Whether to replace path parameters with generated values
        request_logger: Optional request logger for tracking requests and responses

    Returns:
        List of ScanResult objects containing scan results
    """
    logger.debug('Starting API scan', host=host, port=port)

    # Get base URL
    base_url = f"http://{host}:{port}"
    logger.debug('Using base URL', base_url=base_url)

    # Get paths from OpenAPI spec
    paths = data.get('paths', {})
    if not paths:
        logger.warning('No paths found in OpenAPI specification')
        return []

    logger.debug('Found paths to scan', count=len(paths))

    results = []

    # Scan each path
    for path, path_item in paths.items():
        logger.debug('Scanning path', path=path)

        # Get operations for this path
        operations = {
            method: details
            for method, details in path_item.items()
            if method in ['get', 'post', 'put', 'delete', 'patch']
        }

        if not operations:
            logger.warning('No operations found for path', path=path)
            continue

        # Scan each operation
        for method, operation in operations.items():
            logger.debug('Scanning operation', method=method.upper())

            # Get operation ID or use path + method as identifier
            operation_id = operation.get('operationId', f"{path}_{method}")
            logger.debug('Operation ID', operation_id=operation_id)

            # Get request parameters
            parameters = operation.get('parameters', [])
            path_params = [
                param for param in parameters
                if param.get('in') == 'path'
            ]

            # Generate path parameter values if needed
            if replace_params and path_params:
                logger.debug('Generating path parameter values')
                param_values = generate_path_params(path_params)
                request_path = path.format(**param_values)
            else:
                request_path = path
                param_values = None

            # Build request URL
            url = f"{base_url}{request_path}"
            logger.debug('Request URL', url=url)

            # Get request body if present
            request_body = None
            if 'requestBody' in operation:
                content = operation['requestBody'].get('content', {})
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    request_body = generate_request_body(schema)
                    logger.debug('Request body', body=request_body)

            # Make the request
            try:
                # Log the request if logger is provided
                request_id = None
                if request_logger:
                    request_id = request_logger.log_request(
                        method=method,
                        url=url,
                        headers=headers.copy(),  # Copy to avoid modifying original
                        cookies=cookies,
                        body=request_body,
                        path_params=param_values,
                    )

                logger.debug('Making request', method=method.upper(), url=url)
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    cookies=cookies,
                    json=request_body,
                    timeout=30,
                )

                # Log response if logger is provided
                if request_logger and request_id:
                    request_logger.log_response(
                        request_id=request_id,
                        status_code=response.status_code,
                        response_headers=dict(response.headers),
                        response_body=response.text,
                        response_time=response.elapsed.total_seconds(),
                    )

                # Log response
                logger.debug(
                    'Response received',
                    status_code=response.status_code,
                    response_time=response.elapsed.total_seconds(),
                )

                # Add result to list
                results.append(
                    ScanResult(
                        method=method,
                        url=url,
                        status_code=response.status_code,
                        response=response.text,
                        response_time=response.elapsed.total_seconds(),
                    ),
                )

                # Display result
                display_result(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    response=response,
                    response_time=response.elapsed.total_seconds(),
                )

            except requests.RequestException as e:
                logger.error(
                    'Request failed', method=method,
                    url=url, error=str(e),
                )

                # Log error if logger is provided
                if request_logger and request_id:
                    request_logger.log_error(
                        request_id=request_id,
                        error=str(e),
                        error_type='request_error',
                    )

                results.append(
                    ScanResult(
                        method=method,
                        url=url,
                        status_code=None,
                        error=str(e),
                    ),
                )

                # Display error
                display_error(method=method, url=url, error=str(e))

    # Save logs if logger is provided
    if request_logger:
        request_logger.save_logs()

    return results


def generate_request_body(schema: dict[str, Any]) -> dict[str, Any]:
    """Generate a request body based on the schema.

    Args:
        schema: OpenAPI schema for the request body

    Returns:
        Generated request body as a dictionary
    """
    logger.debug('Generating request body from schema')

    # For now, return an empty object
    # TODO: Implement proper request body generation based on schema
    return {}


def display_result(
    method: str,
    url: str,
    status_code: int,
    response: requests.Response,
    response_time: float,
) -> None:
    """Display the result of an API request.

    Args:
        method: HTTP method used
        url: Request URL
        status_code: Response status code
        response: Response object
        response_time: Response time in seconds
    """
    # Create status color based on status code
    if 200 <= status_code < 300:
        status_color = 'green'
    elif 300 <= status_code < 400:
        status_color = 'yellow'
    else:
        status_color = 'red'

    # Create method color
    method_colors = {
        'get': 'blue',
        'post': 'green',
        'put': 'yellow',
        'delete': 'red',
        'patch': 'magenta',
    }
    method_color = method_colors.get(method.lower(), 'white')

    # Create result table
    table = Table(show_header=False, box=None)
    table.add_row(
        Text(method.upper(), style=method_color),
        Text(f"{status_code}", style=status_color),
        Text(f"{response_time:.3f}s", style='cyan'),
        Text(url),
    )

    # Create result panel
    result = Panel(
        table,
        title='API Scan Result',
        border_style=status_color,
    )

    console.print(result)


def display_error(method: str, url: str, error: str) -> None:
    """Display an error that occurred during an API request.

    Args:
        method: HTTP method used
        url: Request URL
        error: Error message
    """
    # Create method color
    method_colors = {
        'get': 'blue',
        'post': 'green',
        'put': 'yellow',
        'delete': 'red',
        'patch': 'magenta',
    }
    method_color = method_colors.get(method.lower(), 'white')

    # Create error table
    table = Table(show_header=False, box=None)
    table.add_row(
        Text(method.upper(), style=method_color),
        Text('ERROR', style='red'),
        Text(url),
    )

    # Create error panel
    result = Panel(
        table,
        title='API Scan Error',
        border_style='red',
    )

    console.print(result)
