"""Tests for the fetcher module."""

from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError, RequestException, Timeout

from cli_dev_toolbox.fetcher import fetch_url, fetch_urls_batch, format_fetch_result


class TestFetchUrl:
    """Test cases for URL fetching."""

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_success(self, mock_get):
        """Test successful URL fetch."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Hello, World!"
        mock_response.text = "Hello, World!"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_get.return_value = mock_response

        # Execute
        result = fetch_url("https://example.com")

        # Assert
        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["content_length"] == 13
        assert result["url"] == "https://example.com"
        assert result["error"] is None
        assert result["response_time_ms"] > 0
        assert "Content-Type" in result["headers"]

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_timeout(self, mock_get):
        """Test URL fetch with timeout."""
        # Setup mock to raise timeout
        mock_get.side_effect = Timeout("Request timed out")

        # Execute
        result = fetch_url("https://example.com", timeout=5)

        # Assert
        assert result["success"] is False
        assert result["status_code"] is None
        assert result["error"] == "Request timed out"
        assert result["response_time_ms"] > 0
        assert result["content_length"] == 0

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_connection_error(self, mock_get):
        """Test URL fetch with connection error."""
        # Setup mock to raise connection error
        mock_get.side_effect = ConnectionError("Connection failed")

        # Execute
        result = fetch_url("https://example.com")

        # Assert
        assert result["success"] is False
        assert result["status_code"] is None
        assert result["error"] == "Connection error"
        assert result["response_time_ms"] > 0
        assert result["content_length"] == 0

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_general_error(self, mock_get):
        """Test URL fetch with general request error."""
        # Setup mock to raise general error
        mock_get.side_effect = RequestException("General error")

        # Execute
        result = fetch_url("https://example.com")

        # Assert
        assert result["success"] is False
        assert result["status_code"] is None
        assert result["error"] == "General error"
        assert result["response_time_ms"] > 0
        assert result["content_length"] == 0

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_with_custom_headers(self, mock_get):
        """Test URL fetch with custom headers."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_response.text = "Success"
        mock_response.headers = {}
        mock_get.return_value = mock_response

        # Execute
        custom_headers = {"Authorization": "Bearer token"}
        result = fetch_url("https://example.com", headers=custom_headers)

        # Assert
        assert result["success"] is True
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer token"
        assert headers["User-Agent"] == "CLI-Dev-Toolbox/1.0"

    @patch("cli_dev_toolbox.fetcher.requests.get")
    def test_fetch_url_with_timeout(self, mock_get):
        """Test URL fetch with custom timeout."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"Success"
        mock_response.text = "Success"
        mock_response.headers = {}
        mock_get.return_value = mock_response

        # Execute
        result = fetch_url("https://example.com", timeout=10)

        # Assert
        assert result["success"] is True
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["timeout"] == 10


class TestFetchUrlsBatch:
    """Test cases for batch URL fetching."""

    @patch("cli_dev_toolbox.fetcher.fetch_url")
    def test_fetch_urls_batch_success(self, mock_fetch_url):
        """Test successful batch URL fetching."""
        # Setup mock responses
        mock_fetch_url.side_effect = [
            {"url": "https://example1.com", "success": True, "status_code": 200},
            {"url": "https://example2.com", "success": True, "status_code": 200},
        ]

        # Execute
        urls = ["https://example1.com", "https://example2.com"]
        results = fetch_urls_batch(urls, max_workers=2)

        # Assert
        assert len(results) == 2
        assert results[0]["url"] == "https://example1.com"
        assert results[1]["url"] == "https://example2.com"
        assert mock_fetch_url.call_count == 2

    @patch("cli_dev_toolbox.fetcher.fetch_url")
    def test_fetch_urls_batch_mixed_results(self, mock_fetch_url):
        """Test batch URL fetching with mixed success/failure."""
        # Setup mock responses
        mock_fetch_url.side_effect = [
            {"url": "https://example1.com", "success": True, "status_code": 200},
            {"url": "https://example2.com", "success": False, "error": "Timeout"},
        ]

        # Execute
        urls = ["https://example1.com", "https://example2.com"]
        results = fetch_urls_batch(urls, max_workers=2)

        # Assert
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[1]["error"] == "Timeout"


class TestFormatFetchResult:
    """Test cases for formatting fetch results."""

    def test_format_fetch_result_success(self):
        """Test formatting successful fetch result."""
        # Setup
        result = {
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 150.5,
            "content_length": 1024,
            "headers": {"Content-Type": "text/html"},
            "content": "<html>...</html>",
            "success": True,
            "error": None,
        }

        # Execute
        formatted = format_fetch_result(result)

        # Assert
        assert "✅ https://example.com" in formatted
        assert "Status: 200" in formatted
        assert "Response Time: 150.5ms" in formatted
        assert "Content Length: 1024 bytes" in formatted

    def test_format_fetch_result_success_verbose(self):
        """Test formatting successful fetch result with verbose output."""
        # Setup
        result = {
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 150.5,
            "content_length": 1024,
            "headers": {"Content-Type": "text/html"},
            "content": "<html>Hello World</html>",
            "success": True,
            "error": None,
        }

        # Execute
        formatted = format_fetch_result(result, verbose=True)

        # Assert
        assert "✅ https://example.com" in formatted
        assert "Status: 200" in formatted
        assert "Response Time: 150.5ms" in formatted
        assert "Content Length: 1024 bytes" in formatted
        assert "Headers: 1 headers" in formatted
        assert "Content Preview: <html>Hello World</html>..." in formatted

    def test_format_fetch_result_failure(self):
        """Test formatting failed fetch result."""
        # Setup
        result = {
            "url": "https://example.com",
            "status_code": None,
            "response_time_ms": 5000.0,
            "content_length": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": "Request timed out",
        }

        # Execute
        formatted = format_fetch_result(result)

        # Assert
        assert "❌ https://example.com" in formatted
        assert "Error: Request timed out" in formatted
        assert "Response Time: 5000.0ms" in formatted
