import time
from typing import Any, Dict, Optional

import requests
from requests.exceptions import RequestException


def fetch_url(
    url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Fetch a URL and return response information including timing.

    :param url: The URL to fetch.
    :param timeout: Request timeout in seconds (default: 30).
    :param headers: Optional headers to include in the request.
    :return: Dictionary containing response information.
    """
    start_time = time.time()

    try:
        # Set default headers if none provided
        if headers is None:
            headers = {}

        # Always include User-Agent
        headers["User-Agent"] = "CLI-Dev-Toolbox/1.0"

        # Make the request
        response = requests.get(url, timeout=timeout, headers=headers)
        end_time = time.time()

        # Calculate response time
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "url": url,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "content_length": len(response.content),
            "headers": dict(response.headers),
            "content": response.text,
            "success": True,
            "error": None,
        }

    except requests.exceptions.Timeout:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": round(response_time, 2),
            "content_length": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": "Request timed out",
        }

    except requests.exceptions.ConnectionError:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": round(response_time, 2),
            "content_length": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": "Connection error",
        }

    except RequestException as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {
            "url": url,
            "status_code": None,
            "response_time_ms": round(response_time, 2),
            "content_length": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": str(e),
        }


def fetch_urls_batch(urls: list, timeout: int = 30, max_workers: int = 5) -> list:
    """
    Fetch multiple URLs in parallel.

    :param urls: List of URLs to fetch.
    :param timeout: Request timeout in seconds (default: 30).
    :param max_workers: Maximum number of concurrent requests (default: 5).
    :return: List of response dictionaries.
    """
    import concurrent.futures

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        future_to_url = {executor.submit(fetch_url, url, timeout): url for url in urls}

        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            result = future.result()
            results.append(result)

    return results


def format_fetch_result(result: Dict[str, Any], verbose: bool = False) -> str:
    """
    Format fetch result for display.

    :param result: Result dictionary from fetch_url.
    :param verbose: Whether to include detailed information.
    :return: Formatted string representation.
    """
    if result["success"]:
        output = [
            f"✅ {result['url']}",
            f"   Status: {result['status_code']}",
            f"   Response Time: {result['response_time_ms']}ms",
            f"   Content Length: {result['content_length']} bytes",
        ]

        if verbose:
            output.extend(
                [
                    f"   Headers: {len(result['headers'])} headers",
                    f"   Content Preview: {result['content'][:100]}...",
                ]
            )
    else:
        output = [
            f"❌ {result['url']}",
            f"   Error: {result['error']}",
            f"   Response Time: {result['response_time_ms']}ms",
        ]

    return "\n".join(output)
