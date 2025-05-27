"""Tests for the command-line interface."""

from typing import List
from unittest import mock
from unittest.mock import MagicMock

import pytest

from salary_reporter import cli
from salary_reporter.domain_models import EmployeeData
from salary_reporter.exceptions import SalaryReporterError


def test_parse_arguments_basic() -> None:
    """Test basic argument parsing."""
    args = cli.parse_arguments(["file1.csv", "file2.csv", "--report", "payout"])
    assert args.csv_files == ["file1.csv", "file2.csv"]
    assert args.report == "payout"


def test_parse_arguments_default_report() -> None:
    """Test default report type."""
    args = cli.parse_arguments(["file.csv"])
    assert args.report == "payout"


def test_parse_arguments_invalid_report(capsys: pytest.CaptureFixture) -> None:
    """Test invalid report type choice."""
    with pytest.raises(SystemExit) as excinfo:  # argparse exits on error
        cli.parse_arguments(["file.csv", "--report", "invalid_report_type"])
    # Argparse exits with code 2 for argument errors
    assert excinfo.value.code == 2
    # Check stderr for error message (argparse prints to stderr)
    captured = capsys.readouterr()
    assert "invalid choice: 'invalid_report_type'" in captured.err


def test_parse_arguments_missing_files(capsys: pytest.CaptureFixture) -> None:
    """Test missing required file arguments."""
    with pytest.raises(SystemExit) as excinfo:
        cli.parse_arguments(["--report", "payout"])
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "the following arguments are required: FILE" in captured.err


@mock.patch("salary_reporter.cli.CSVDataLoader")
@mock.patch("salary_reporter.cli.get_report_configuration")
def test_main_logic_success(
    mock_get_config: MagicMock,
    mock_data_loader_cls: MagicMock,
    sample_employee_data_list: List[EmployeeData],
) -> None:
    """Test successful execution of main_logic."""
    # Mock instances and their methods
    mock_loader_instance = mock_data_loader_cls.return_value
    mock_loader_instance.load_all_data.return_value = sample_employee_data_list

    mock_generator_cls = mock.MagicMock()
    mock_formatter_cls = mock.MagicMock()
    mock_generator_instance = mock_generator_cls.return_value
    mock_formatter_instance = mock_formatter_cls.return_value

    # Mock ReportConfiguration object
    mock_report_config_obj = mock.Mock()
    mock_report_config_obj.generator_cls = mock_generator_cls
    mock_report_config_obj.formatter_cls = mock_formatter_cls
    mock_get_config.return_value = mock_report_config_obj

    mock_generator_instance.generate.return_value = {"some": "raw_data"}
    mock_formatter_instance.format.return_value = "Formatted Report"

    args_namespace = mock.Mock(spec=cli.argparse.Namespace)
    args_namespace.csv_files = ["file1.csv"]
    args_namespace.report = "payout"

    result = cli.main_logic(args_namespace)

    mock_loader_instance.load_all_data.assert_called_once_with(["file1.csv"])
    mock_get_config.assert_called_once_with("payout")
    mock_generator_instance.generate.assert_called_once_with(sample_employee_data_list)
    mock_formatter_instance.format.assert_called_once_with({"some": "raw_data"})
    assert result == "Formatted Report"


@mock.patch("salary_reporter.cli.CSVDataLoader")
def test_main_logic_no_data(mock_data_loader_cls: MagicMock) -> None:
    """Test main_logic when no employee data is found."""
    mock_loader_instance = mock_data_loader_cls.return_value
    mock_loader_instance.load_all_data.return_value = []

    args_namespace = mock.Mock(spec=cli.argparse.Namespace)
    args_namespace.csv_files = ["empty.csv"]
    args_namespace.report = "payout"

    result = cli.main_logic(args_namespace)
    assert result == "No employee data found in the provided files."


@mock.patch("salary_reporter.cli.parse_arguments")
@mock.patch("salary_reporter.cli.main_logic")
def test_run_success(
    mock_main_logic: MagicMock,
        mock_parse_args: MagicMock,
        capsys: pytest.CaptureFixture
) -> None:
    """Test successful run of the CLI entry point."""
    args_namespace = mock.Mock(spec=cli.argparse.Namespace)
    args_namespace.csv_files = ["f.csv"]
    args_namespace.report = "payout"
    mock_parse_args.return_value = args_namespace
    mock_main_logic.return_value = "Test Report Output"

    cli.run()

    captured = capsys.readouterr()
    assert "Test Report Output" in captured.out
    mock_main_logic.assert_called_once_with(args_namespace)
    mock_parse_args.assert_called_once()


@mock.patch("salary_reporter.cli.parse_arguments")
@mock.patch(
    "salary_reporter.cli.main_logic",
    side_effect=SalaryReporterError("Test Error")
)
def test_run_salary_reporter_error(
        mock_main_logic: MagicMock,
        mock_parse_args: MagicMock,
        capsys: pytest.CaptureFixture
) -> None:
    """Test CLI run with a known SalaryReporterError."""
    args_namespace = mock.Mock(spec=cli.argparse.Namespace)
    mock_parse_args.return_value = args_namespace

    with pytest.raises(SystemExit) as excinfo:
        cli.run()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error: Test Error" in captured.err

    mock_parse_args.assert_called_once()
    mock_main_logic.assert_called_once_with(args_namespace)


@mock.patch("salary_reporter.cli.parse_arguments")
@mock.patch(
    "salary_reporter.cli.main_logic", side_effect=Exception("Unexpected Kaboom")
)
def test_run_unexpected_error(
        mock_main_logic: MagicMock,
        mock_parse_args: MagicMock,
        capsys: pytest.CaptureFixture
) -> None:
    """Test CLI run with an unexpected generic exception."""
    args_namespace = mock.Mock(spec=cli.argparse.Namespace)
    mock_parse_args.return_value = args_namespace

    with pytest.raises(SystemExit) as excinfo:
        cli.run()
    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "An unexpected error occurred: Unexpected Kaboom" in captured.err
    mock_parse_args.assert_called_once()

    mock_parse_args.assert_called_once()
    mock_main_logic.assert_called_once_with(args_namespace)
