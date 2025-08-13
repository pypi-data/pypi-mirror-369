"""Tests for the converters module."""

import csv
import json

import pytest

from cli_dev_toolbox.converters import json_to_csv, pretty_print_json, validate_json


class TestJsonToCsv:
    """Test cases for JSON to CSV conversion."""

    def test_basic_json_to_csv(self, tmp_path):
        """Test basic JSON to CSV conversion."""
        # Setup
        json_data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "Los Angeles"},
        ]
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        json_to_csv(str(json_file), str(csv_file))

        # Assert
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"
        assert rows[0]["city"] == "New York"
        assert rows[1]["name"] == "Bob"
        assert rows[1]["age"] == "25"
        assert rows[1]["city"] == "Los Angeles"

    def test_nested_json_structure(self, tmp_path):
        """Test JSON with nested structure."""
        # Setup
        json_data = {
            "emp_details": [
                {"id": 1, "name": "Alice", "department": "Engineering"},
                {"id": 2, "name": "Bob", "department": "Marketing"},
            ]
        }
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        json_to_csv(str(json_file), str(csv_file))

        # Assert
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["name"] == "Alice"
        assert rows[0]["department"] == "Engineering"

    def test_empty_json_array(self, tmp_path):
        """Test conversion of empty JSON array."""
        # Setup
        json_data = []
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        json_to_csv(str(json_file), str(csv_file))

        # Assert
        assert csv_file.exists()

        # Verify CSV content (should only have headers)
        with open(csv_file, "r") as f:
            content = f.read().strip()
            assert content == ""  # Empty file

    def test_missing_input_file(self, tmp_path):
        """Test error handling for missing input file."""
        csv_file = tmp_path / "test.csv"

        with pytest.raises(FileNotFoundError):
            json_to_csv("nonexistent.json", str(csv_file))

    def test_invalid_json_format(self, tmp_path):
        """Test error handling for invalid JSON format."""
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        # Write invalid JSON
        with open(json_file, "w") as f:
            f.write('{"name": "Alice", "age": 30,}')  # Trailing comma

        with pytest.raises(json.JSONDecodeError):
            json_to_csv(str(json_file), str(csv_file))

    def test_different_data_types(self, tmp_path):
        """Test conversion with different data types."""
        # Setup
        json_data = [
            {
                "string": "text",
                "integer": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "list": ["item1", "item2"],
            }
        ]
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        json_to_csv(str(json_file), str(csv_file))

        # Assert
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["string"] == "text"
        assert rows[0]["integer"] == "42"
        assert rows[0]["float"] == "3.14"
        assert rows[0]["boolean"] == "True"
        assert rows[0]["null"] == ""
        assert rows[0]["list"] == "['item1', 'item2']"

    def test_large_dataset(self, tmp_path):
        """Test conversion of large dataset."""
        # Setup
        json_data = [
            {"id": i, "name": f"User{i}", "value": i * 10} for i in range(1000)
        ]
        json_file = tmp_path / "test.json"
        csv_file = tmp_path / "test.csv"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        json_to_csv(str(json_file), str(csv_file))

        # Assert
        assert csv_file.exists()

        # Verify CSV content
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1000
        assert rows[0]["id"] == "0"
        assert rows[0]["name"] == "User0"
        assert rows[0]["value"] == "0"
        assert rows[999]["id"] == "999"
        assert rows[999]["name"] == "User999"
        assert rows[999]["value"] == "9990"


class TestPrettyPrintJson:
    """Test cases for pretty JSON printing."""

    def test_pretty_print_json_to_stdout(self, tmp_path, capsys):
        """Test pretty printing JSON to stdout."""
        # Setup
        json_data = {"name": "Alice", "age": 30, "city": "New York"}
        json_file = tmp_path / "test.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Execute
        result = pretty_print_json(str(json_file))

        # Assert
        captured = capsys.readouterr()
        assert "name" in captured.out
        assert "Alice" in captured.out
        assert "age" in captured.out
        assert "30" in captured.out
        assert result is not None

    def test_pretty_print_json_to_file(self, tmp_path):
        """Test pretty printing JSON to file."""
        # Setup
        json_data = {"name": "Alice", "age": 30, "city": "New York"}
        json_file = tmp_path / "test.json"
        output_file = tmp_path / "formatted.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Execute
        result = pretty_print_json(str(json_file), str(output_file))

        # Assert
        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
            assert "name" in content
            assert "Alice" in content
            assert "age" in content
            assert "30" in content
            assert result is not None

    def test_pretty_print_json_with_custom_indent(self, tmp_path):
        """Test pretty printing JSON with custom indentation."""
        # Setup
        json_data = {"name": "Alice", "age": 30}
        json_file = tmp_path / "test.json"
        output_file = tmp_path / "formatted.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f, separators=(",", ":"))

        # Execute
        pretty_print_json(str(json_file), str(output_file), indent=4)

        # Assert
        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
            # Check for 4-space indentation
            lines = content.split("\n")
            # JSON keys are sorted, so check for both possible orders
            assert any(
                '    "' in line for line in lines[1:3]
            )  # Check for 4 spaces in first few lines

    def test_pretty_print_json_missing_file(self, tmp_path):
        """Test error handling for missing input file."""
        output_file = tmp_path / "output.json"

        with pytest.raises(FileNotFoundError):
            pretty_print_json("nonexistent.json", str(output_file))

    def test_pretty_print_json_invalid_json(self, tmp_path):
        """Test error handling for invalid JSON."""
        json_file = tmp_path / "invalid.json"
        output_file = tmp_path / "output.json"

        # Write invalid JSON
        with open(json_file, "w") as f:
            f.write('{"name": "Alice", "age": 30,}')  # Trailing comma

        with pytest.raises(json.JSONDecodeError):
            pretty_print_json(str(json_file), str(output_file))


class TestValidateJson:
    """Test cases for JSON validation."""

    def test_validate_json_valid_file(self, tmp_path):
        """Test validation of valid JSON file."""
        # Setup
        json_data = {"name": "Alice", "age": 30}
        json_file = tmp_path / "test.json"

        with open(json_file, "w") as f:
            json.dump(json_data, f)

        # Execute
        result = validate_json(str(json_file))

        # Assert
        assert result is True

    def test_validate_json_invalid_file(self, tmp_path):
        """Test validation of invalid JSON file."""
        # Setup
        json_file = tmp_path / "invalid.json"

        with open(json_file, "w") as f:
            f.write('{"name": "Alice", "age": 30,}')  # Trailing comma

        # Execute
        result = validate_json(str(json_file))

        # Assert
        assert result is False

    def test_validate_json_missing_file(self):
        """Test validation of missing file."""
        # Execute
        result = validate_json("nonexistent.json")

        # Assert
        assert result is False
