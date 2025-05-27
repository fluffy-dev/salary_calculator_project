"""Command-line interface for the salary reporter."""

import argparse
import sys
from typing import List, Optional

from salary_reporter.data_loader import CSVDataLoader
from salary_reporter.exceptions import SalaryReporterError
from salary_reporter.reporting.registry import (
    get_available_reports,
    get_report_configuration,
)


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses command-line arguments.

    Args:
        args: Optional list of arguments to parse. Defaults to sys.argv[1:].

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generates salary reports from CSV files."
    )
    parser.add_argument(
        "csv_files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="One or more CSV files containing employee data.",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="payout",
        choices=get_available_reports(),
        help=(
            "The type of report to generate. "
            f"Default: 'payout'. Available: {', '.join(get_available_reports())}"
        ),
    )
    # Add --output-format here if JSON/other outputs were to be supported via CLI
    # parser.add_argument(
    #     "--output-format", type=str, default="console", choices=["console", "json"]
    # )
    return parser.parse_args(args)


def main_logic(args: argparse.Namespace) -> str:
    """
    Core logic for loading data, generating, and formatting the report.

    Args:
        args: Parsed command-line arguments.

    Returns:
        The formatted report as a string.

    Raises:
        SalaryReporterError: If any error occurs during the process.
    """
    data_loader = CSVDataLoader()
    employee_data = data_loader.load_all_data(args.csv_files)

    if not employee_data:
        return "No employee data found in the provided files."

    report_config = get_report_configuration(args.report)

    generator = report_config.generator_cls()
    formatter = report_config.formatter_cls()

    raw_report_data = generator.generate(employee_data)
    formatted_report = formatter.format(raw_report_data)

    return formatted_report


def run() -> None:
    """
    Entry point for the CLI application.

    Parses arguments, executes main logic, and prints output or errors.
    """
    try:
        arguments = parse_arguments()
        report_output = main_logic(arguments)
        print(report_output)
    except SalaryReporterError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(2)
