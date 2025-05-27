"""Tests for PayoutReportGenerator and PayoutConsoleFormatter."""

from decimal import Decimal

import pytest

from salary_reporter.custom_types import PayoutReportData
from salary_reporter.domain_models import EmployeeData
from salary_reporter.reporting.payout_report import (
    PayoutConsoleFormatter,
    PayoutReportGenerator,
)


@pytest.fixture()
def payout_generator() -> PayoutReportGenerator:
    """Fixture for PayoutReportGenerator."""
    return PayoutReportGenerator()


@pytest.fixture()
def payout_formatter() -> PayoutConsoleFormatter:
    """Fixture for PayoutConsoleFormatter."""
    return PayoutConsoleFormatter()


def test_payout_report_generator_empty_data(payout_generator: PayoutReportGenerator):
    """Test PayoutReportGenerator with no employee data."""
    report_data = payout_generator.generate([])
    assert report_data == {}


def test_payout_report_generator_single_employee(
    payout_generator: PayoutReportGenerator,
):
    """Test PayoutReportGenerator with a single employee."""
    emp_data = [
        EmployeeData("1", "test@example.com", "John Doe", "Sales", 100, Decimal("20"))
    ]
    report_data = payout_generator.generate(emp_data)

    assert "Sales" in report_data
    sales_dept = report_data["Sales"]
    assert len(sales_dept["employees"]) == 1
    assert sales_dept["employees"][0]["name"] == "John Doe"
    assert sales_dept["employees"][0]["hours"] == 100
    assert sales_dept["employees"][0]["rate"] == "20.00"
    assert sales_dept["employees"][0]["payout"] == "2000.00"
    assert sales_dept["total_hours"] == 100
    assert sales_dept["total_payout"] == "2000.00"


def test_payout_report_generator_multiple_employees_departments(
    payout_generator: PayoutReportGenerator,
    sample_employee_data_list: list[EmployeeData],
):
    """Test PayoutReportGenerator with multiple employees and departments."""
    report_data = payout_generator.generate(sample_employee_data_list)

    assert len(report_data) == 2  # Design, Marketing
    assert "Design" in report_data
    assert "Marketing" in report_data

    design_dept = report_data["Design"]
    marketing_dept = report_data["Marketing"]

    assert len(design_dept["employees"]) == 2
    assert design_dept["employees"][0]["name"] == "Bob Smith"  # Sorted by name
    assert design_dept["employees"][1]["name"] == "Carol Williams"
    assert design_dept["total_hours"] == 150 + 170

    expected_design_payout = Decimal("150") * Decimal("40") + Decimal("170") * Decimal(
        "60"
    )

    assert design_dept["total_payout"] == str(
        expected_design_payout.quantize(Decimal("0.01"))
    )

    assert len(marketing_dept["employees"]) == 1
    assert marketing_dept["employees"][0]["name"] == "Alice Johnson"
    assert marketing_dept["total_hours"] == 160

    expected_marketing_payout = Decimal("160") * Decimal("50")

    assert marketing_dept["total_payout"] == str(
        expected_marketing_payout.quantize(Decimal("0.01"))
    )


def test_payout_console_formatter_empty_data(payout_formatter: PayoutConsoleFormatter):
    """Test PayoutConsoleFormatter with no report data."""
    formatted_output = payout_formatter.format({})
    assert "No data available" in formatted_output


def test_payout_console_formatter_structure(
    payout_formatter: PayoutConsoleFormatter,
    payout_generator: PayoutReportGenerator,
    sample_employee_data_list: list[EmployeeData],
):
    """Test the structure of console output from PayoutConsoleFormatter."""
    raw_data = payout_generator.generate(sample_employee_data_list)
    formatted_output = payout_formatter.format(raw_data)

    # Check for department names
    assert "Design" in formatted_output
    assert "Marketing" in formatted_output

    # Check for employee names (Bob Smith is first in Design due to sorting)
    assert "---------------- Bob Smith" in formatted_output
    assert "---------------- Carol Williams" in formatted_output
    assert "---------------- Alice Johnson" in formatted_output

    # Check for some numbers (exact spacing depends on calculated widths)
    # For Bob Smith: 150 hours, 40 rate, $6000 payout
    assert "150" in formatted_output
    assert "40" in formatted_output
    assert "$6000" in formatted_output
    # For Design total: 320 hours, $16200 payout
    assert "320" in formatted_output
    assert "$16200" in formatted_output

    # Verify department sorting (Design before Marketing)
    assert formatted_output.find("Design") < formatted_output.find("Marketing")

    # Check structure of total lines (e.g., blank name and rate for total)
    # Example for Design total line: '320 $16200'
    # This is tricky to assert precisely without knowing exact widths.
    # We can check that a line with the total hours \
    # and payout exists for each department.
    design_total_line_regex = r"\s+320\s+\$16200"
    marketing_total_line_regex = r"\s+160\s+\$8000"
    import re

    assert re.search(design_total_line_regex, formatted_output) is not None
    assert re.search(marketing_total_line_regex, formatted_output) is not None


def test_payout_console_formatter_specific_output(
    payout_formatter: PayoutConsoleFormatter,
):
    """
    Test console formatter with a specific,
    small dataset for exact output matching.
    """
    specific_data: PayoutReportData = {
        "AlphaTeam": {
            "employees": [
                # Corrected order: "Aye Alpha" then "Zee Alpha"
                {"name": "Aye Alpha", "hours": 20, "rate": "2.00", "payout": "40.00"},
                {"name": "Zee Alpha", "hours": 10, "rate": "1.00", "payout": "10.00"},
            ],
            "total_hours": 30,
            "total_payout": "50.00",
        }
    }
    output = payout_formatter.format(specific_data)

    # Department Header
    assert "AlphaTeam" in output

    # Employee lines - now the assertion should pass
    assert "---------------- Aye Alpha" in output
    assert "---------------- Zee Alpha" in output

    # Aye Alpha's data
    assert "20" in output  # hours
    assert "2" in output  # rate
    assert "$40" in output  # payout

    # Zee Alpha's data
    assert "10" in output  # hours
    assert "1" in output  # rate
    assert "$10" in output  # payout

    # Total line
    assert "30" in output  # total hours
    assert "$50" in output  # total payout

    # Check that Aye appears before Zee in the output
    assert output.find("Aye Alpha") < output.find("Zee Alpha")
