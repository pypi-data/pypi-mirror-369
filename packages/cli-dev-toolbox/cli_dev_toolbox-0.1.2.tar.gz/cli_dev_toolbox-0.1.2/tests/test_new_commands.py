"""Tests for the new prettyjson and fetch commands."""

import json
import sys
from unittest.mock import patch

from cli_dev_toolbox.toolbox import main


class TestPrettyJsonCommand:
    """Test cases for the prettyjson command."""

    def test_prettyjson_command_to_stdout(self, tmp_path, capsys):
        """Test prettyjson command output to stdout."""
        # Setup test data
        json_data = {"name": "Alice", "age": 30}
        json_file = tmp_path / "test.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "prettyjson", str(json_file)]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        captured = capsys.readouterr()
        assert "JSON formatted and printed to stdout" in captured.out
        assert "name" in captured.out
        assert "Alice" in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    def test_prettyjson_command_to_file(self, tmp_path, capsys):
        """Test prettyjson command output to file."""
        # Setup test data
        json_data = {"name": "Alice", "age": 30}
        json_file = tmp_path / "test.json"
        output_file = tmp_path / "formatted.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "prettyjson", str(json_file), "-o", str(output_file)]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        assert output_file.exists()
        captured = capsys.readouterr()
        assert "Formatted JSON saved to" in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    def test_prettyjson_command_with_custom_indent(self, tmp_path, capsys):
        """Test prettyjson command with custom indentation."""
        # Setup test data
        json_data = {"name": "Alice", "age": 30}
        json_file = tmp_path / "test.json"
        output_file = tmp_path / "formatted.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = [
            "toolbox",
            "prettyjson",
            str(json_file),
            "-o",
            str(output_file),
            "-i",
            "4",
        ]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
            lines = content.split("\n")
            # JSON keys are sorted, so check for 4-space indentation in any of the
            # first few lines
            assert any('    "' in line for line in lines[1:3])  # Check for 4 spaces

        # Restore sys.argv
        sys.argv = original_argv


class TestFetchCommand:
    """Test cases for the fetch command."""

    @patch("cli_dev_toolbox.toolbox.fetch_url")
    def test_fetch_command_success(self, mock_fetch_url, capsys):
        """Test fetch command with successful response."""
        # Setup mock response
        mock_fetch_url.return_value = {
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 150.5,
            "content_length": 1024,
            "headers": {},
            "content": "Hello World",
            "success": True,
            "error": None,
        }

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "fetch", "https://example.com"]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        captured = capsys.readouterr()
        assert "✅ https://example.com" in captured.out
        assert "Status: 200" in captured.out
        assert "Response Time: 150.5ms" in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    @patch("cli_dev_toolbox.toolbox.fetch_url")
    def test_fetch_command_with_timeout(self, mock_fetch_url, capsys):
        """Test fetch command with custom timeout."""
        # Setup mock response
        mock_fetch_url.return_value = {
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 100.0,
            "content_length": 512,
            "headers": {},
            "content": "Success",
            "success": True,
            "error": None,
        }

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "fetch", "https://example.com", "-t", "10"]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        mock_fetch_url.assert_called_once_with("https://example.com", 10)
        captured = capsys.readouterr()
        assert "✅ https://example.com" in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    @patch("cli_dev_toolbox.toolbox.fetch_url")
    def test_fetch_command_with_verbose(self, mock_fetch_url, capsys):
        """Test fetch command with verbose output."""
        # Setup mock response
        mock_fetch_url.return_value = {
            "url": "https://example.com",
            "status_code": 200,
            "response_time_ms": 150.5,
            "content_length": 1024,
            "headers": {"Content-Type": "text/html"},
            "content": "Hello World",
            "success": True,
            "error": None,
        }

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "fetch", "https://example.com", "-v"]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        captured = capsys.readouterr()
        assert "✅ https://example.com" in captured.out
        assert "Status: 200" in captured.out
        assert "Headers: 1 headers" in captured.out
        assert "Content Preview: Hello World..." in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    @patch("cli_dev_toolbox.toolbox.fetch_url")
    def test_fetch_command_failure(self, mock_fetch_url, capsys):
        """Test fetch command with failed response."""
        # Setup mock response
        mock_fetch_url.return_value = {
            "url": "https://example.com",
            "status_code": None,
            "response_time_ms": 5000.0,
            "content_length": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": "Request timed out",
        }

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "fetch", "https://example.com"]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        captured = capsys.readouterr()
        assert "❌ https://example.com" in captured.out
        assert "Error: Request timed out" in captured.out
        assert "Response Time: 5000.0ms" in captured.out

        # Restore sys.argv
        sys.argv = original_argv
