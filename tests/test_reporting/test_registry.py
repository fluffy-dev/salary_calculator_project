"""Tests for the report registry."""

import pytest

from salary_reporter.exceptions import UnsupportedReportTypeError
from salary_reporter.reporting.payout_report import (
    PayoutConsoleFormatter,
    PayoutReportGenerator,
)
from salary_reporter.reporting.registry import (
    get_available_reports,
    get_report_configuration,
)


def test_get_report_configuration_payout():
    """Test retrieving configuration for the 'payout' report."""
    config = get_report_configuration("payout")
    assert config.generator_cls == PayoutReportGenerator
    assert config.formatter_cls == PayoutConsoleFormatter

    config_upper = get_report_configuration("PAYOUT")  # Case-insensitivity
    assert config_upper.generator_cls == PayoutReportGenerator


def test_get_report_configuration_unsupported():
    """Test retrieving configuration for an unsupported report type."""
    with pytest.raises(UnsupportedReportTypeError) as excinfo:
        get_report_configuration("unknown_report")
    assert "Report type 'unknown_report' is not supported" in str(excinfo.value)
    assert "payout" in str(excinfo.value)  # Ensure available reports are listed


def test_get_available_reports():
    """Test retrieving the list of available reports."""
    available = get_available_reports()
    assert "payout" in available
    assert isinstance(available, list)
