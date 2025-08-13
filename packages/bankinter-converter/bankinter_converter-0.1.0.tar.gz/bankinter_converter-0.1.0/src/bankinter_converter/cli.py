#!/usr/bin/env python3
"""Command line interface for Bankinter converter."""

import argparse
import sys
from pathlib import Path

from .checking_account import CheckingAccountConverter
from .credit_card import CreditCardConverter


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert Bankinter bank statements (checking accounts and credit cards) from Excel to CSV"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Checking account converter
    checking_parser = subparsers.add_parser(
        "checking", help="Convert checking account statements"
    )
    checking_parser.add_argument(
        "input_file",
        help="Path to the input XLS file",
        type=Path,
    )
    checking_parser.add_argument(
        "output_file",
        help="Path to the output CSV file",
        type=Path,
    )
    checking_parser.add_argument(
        "--skip-rows",
        type=int,
        default=3,
        help="Number of rows to skip from the beginning (default: 3)",
    )
    checking_parser.add_argument(
        "--columns",
        type=str,
        default="A:E",
        help="Columns to include in output (default: A:E)",
    )
    checking_parser.add_argument(
        "--sheet",
        type=str,
        default=0,
        help="Sheet name or index to process (default: 0)",
    )
    checking_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    # Credit card converter
    credit_parser = subparsers.add_parser(
        "credit", help="Convert credit card statements"
    )
    credit_parser.add_argument(
        "input_file",
        help="Path to the input XLS file",
        type=Path,
    )
    credit_parser.add_argument(
        "output_file",
        help="Path to the output CSV file",
        type=Path,
    )
    credit_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def validate_input_file(input_file: Path) -> None:
    """Validate that the input file exists."""
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)


def ensure_output_directory(output_file: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_file.parent.mkdir(parents=True, exist_ok=True)


def run_conversion(args: argparse.Namespace) -> None:
    """Run the appropriate conversion based on the command."""
    try:
        if args.command == "checking":
            converter = CheckingAccountConverter()
            converter.convert_statement(
                input_file=args.input_file,
                output_file=args.output_file,
                skip_rows=args.skip_rows,
                columns=args.columns,
                sheet=args.sheet,
                verbose=args.verbose,
            )
        elif args.command == "credit":
            converter = CreditCardConverter()
            converter.convert_statement(
                input_file=args.input_file,
                output_file=args.output_file,
                verbose=args.verbose,
            )

        # Print success message
        if args.verbose:
            print(f"Successfully converted '{args.input_file}' to '{args.output_file}'")
        else:
            print(f"Converted: {args.output_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate input file
    validate_input_file(args.input_file)

    # Ensure output directory exists
    ensure_output_directory(args.output_file)

    # Run conversion
    run_conversion(args)


if __name__ == "__main__":
    main()
