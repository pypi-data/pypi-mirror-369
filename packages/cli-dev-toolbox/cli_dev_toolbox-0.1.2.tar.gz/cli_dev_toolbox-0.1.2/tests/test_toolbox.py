"""Tests for the main toolbox CLI module."""

import subprocess
import sys

import pytest

from cli_dev_toolbox.toolbox import main


class TestToolboxCLI:
    """Test cases for the main CLI interface."""

    def test_help_output(self, capsys):
        """Test help output."""
        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "--help"]

        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = original_argv

        captured = capsys.readouterr()
        assert "CLI Dev Toolbox" in captured.out
        assert "json2csv" in captured.out
        assert "prettyjson" in captured.out
        assert "fetch" in captured.out

    def test_json2csv_command(self, tmp_path, capsys):
        """Test json2csv command."""
        # Setup test data
        json_data = [{"name": "Alice", "age": 30}]
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            import json

            json.dump(json_data, f)

        # Mock sys.argv
        original_argv = sys.argv
        sys.argv = ["toolbox", "json2csv", str(json_file), str(csv_file)]

        try:
            main()
        except SystemExit:
            pass

        # Assert
        assert csv_file.exists()

        # Check success message
        captured = capsys.readouterr()
        assert "Successfully converted" in captured.out

        # Restore sys.argv
        sys.argv = original_argv

    def test_invalid_command(self, capsys):
        """Test invalid command handling."""
        # Mock sys.argv with invalid command
        original_argv = sys.argv
        sys.argv = ["toolbox", "invalid_command"]

        try:
            main()
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "usage: toolbox" in captured.err

        # Restore sys.argv
        sys.argv = original_argv

    def test_missing_arguments(self, capsys):
        """Test missing arguments handling."""
        # Mock sys.argv with missing arguments
        original_argv = sys.argv
        sys.argv = ["toolbox", "json2csv"]  # Missing input and output files

        try:
            main()
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "error" in captured.err.lower()

        # Restore sys.argv
        sys.argv = original_argv


class TestCLIExecution:
    """Test CLI execution as a subprocess."""

    def test_cli_help(self):
        """Test CLI help command."""
        result = subprocess.run(
            [sys.executable, "-m", "cli_dev_toolbox.toolbox", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "CLI Dev Toolbox" in result.stdout
        assert "json2csv" in result.stdout

    def test_json2csv_subprocess(self, tmp_path):
        """Test json2csv command via subprocess."""
        # Setup test data
        json_data = [{"name": "Alice", "age": 30}]
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            import json

            json.dump(json_data, f)

        # Execute CLI command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "cli_dev_toolbox.toolbox",
                "json2csv",
                str(json_file),
                str(csv_file),
            ],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode == 0
        assert csv_file.exists()

    def test_invalid_json_file(self, tmp_path):
        """Test handling of invalid JSON file."""
        # Create invalid JSON file
        json_file = tmp_path / "invalid.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            f.write('{"name": "Alice", "age": 30,}')  # Invalid JSON

        # Execute CLI command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "cli_dev_toolbox.toolbox",
                "json2csv",
                str(json_file),
                str(csv_file),
            ],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode != 0
        assert "error" in result.stderr.lower()

    def test_missing_input_file(self, tmp_path):
        """Test handling of missing input file."""
        csv_file = tmp_path / "test.csv"

        # Execute CLI command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "cli_dev_toolbox.toolbox",
                "json2csv",
                "nonexistent.json",
                str(csv_file),
            ],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode != 0
        assert "error" in result.stderr.lower()
