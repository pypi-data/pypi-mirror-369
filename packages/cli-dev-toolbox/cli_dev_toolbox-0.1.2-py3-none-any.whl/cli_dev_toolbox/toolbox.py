import argparse

from .converters import json_to_csv, pretty_print_json
from .fetcher import fetch_url, format_fetch_result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI Dev Toolbox - A Python CLI utility for developers"
    )
    subparsers = parser.add_subparsers(dest="command")

    parser_csv = subparsers.add_parser("json2csv")
    parser_csv.add_argument("input", help="Path to JSON file")
    parser_csv.add_argument("output", help="Path to CSV file")

    parser_pretty = subparsers.add_parser("prettyjson")
    parser_pretty.add_argument("input", help="Path to JSON file")
    parser_pretty.add_argument(
        "-o", "--output", help="Output file (if not specified, prints to stdout)"
    )
    parser_pretty.add_argument(
        "-i", "--indent", type=int, default=2, help="Indentation spaces (default: 2)"
    )

    parser_fetch = subparsers.add_parser("fetch")
    parser_fetch.add_argument("url", help="URL to fetch")
    parser_fetch.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    parser_fetch.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed response information",
    )

    args = parser.parse_args()

    if args.command == "json2csv":
        json_to_csv(args.input, args.output)
        print(f"✅ Successfully converted {args.input} to {args.output}")
    elif args.command == "prettyjson":
        pretty_print_json(args.input, args.output, args.indent)
        if args.output:
            print(f"✅ Formatted JSON saved to {args.output}")
        else:
            print("✅ JSON formatted and printed to stdout")
    elif args.command == "fetch":
        result = fetch_url(args.url, args.timeout)
        print(format_fetch_result(result, args.verbose))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
