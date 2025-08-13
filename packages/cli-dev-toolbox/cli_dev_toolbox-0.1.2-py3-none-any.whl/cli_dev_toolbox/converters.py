import csv
import json
from typing import Optional


def json_to_csv(input_file: str, output_file: str) -> None:
    """
    Convert JSON file to CSV format.

    :param input_file: Path to the input JSON file.
    :param output_file: Path to the output CSV file.
    """
    with open(input_file, "r") as f:
        data = json.load(f)

    # Flatten nested structure if needed
    if isinstance(data, dict):
        # If data is a dict, look for list values
        for key, value in data.items():
            if isinstance(value, list):
                data = value
                break
        else:
            # If no list found, wrap the dict in a list
            data = [data]

    if not data:
        # Create empty CSV file
        with open(output_file, "w", newline="") as f:
            f.write("")
        return

    # Get fieldnames from the first item
    fieldnames = list(data[0].keys())

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Successfully converted {input_file} to {output_file}")


def pretty_print_json(
    input_file: str, output_file: Optional[str] = None, indent: int = 2
) -> str:
    """
    Format JSON file with proper indentation for better readability.

    :param input_file: Path to the input JSON file.
    :param output_file: Path to the output JSON file (optional, if None prints to
        stdout).
    :param indent: Number of spaces for indentation (default: 2).
    :return: Formatted JSON string.
    """
    with open(input_file, "r") as f:
        data = json.load(f)

    formatted_json = json.dumps(data, indent=indent, sort_keys=True, ensure_ascii=False)

    if output_file:
        with open(output_file, "w") as f:
            f.write(formatted_json)
        return formatted_json
    else:
        print(formatted_json)
        return formatted_json


def validate_json(input_file: str) -> bool:
    """
    Validate if a file contains valid JSON.

    :param input_file: Path to the JSON file to validate.
    :return: True if valid JSON, False otherwise.
    """
    try:
        with open(input_file, "r") as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False
