"""
Implementation of the Payout Report.

Includes the generator for processing data into the payout report structure
and the formatter for console output.
"""

from collections import defaultdict
from decimal import Decimal
from typing import Dict, List

from salary_reporter.custom_types import (
    DepartmentPayoutSummary,
    EmployeeDataList,
    EmployeePayoutDetail,
    PayoutReportData,
)
from salary_reporter.domain_models import EmployeeData
from salary_reporter.reporting.base import (
    ReportFormatterStrategy,
    ReportGeneratorStrategy,
)


class PayoutReportGenerator(
    ReportGeneratorStrategy[EmployeeDataList, PayoutReportData]
):
    """Generates data for the employee payout report."""

    def generate(self, data: EmployeeDataList) -> PayoutReportData:
        """
        Generates a payout report, grouping employees by department.

        Calculates individual payouts and department totals for hours and payout.

        Args:
            data: A list of EmployeeData objects.

        Returns:
            A dictionary where keys are department names. Each value is
            another dictionary containing a list of employee payout details
            and department totals.
        """
        department_data: Dict[str, Dict[str, List[EmployeeData] | Decimal | int]] = (
            defaultdict(
                lambda: {"employees": [], "total_hours": 0, "total_payout": Decimal(0)}
            )
        )

        for emp in data:
            department_data[emp.department]["employees"].append(emp)

        processed_report: PayoutReportData = {}
        for dept_name, semp_list_and_totals in department_data.items():
            employees_in_dept = semp_list_and_totals["employees"]
            if not isinstance(employees_in_dept, list):  # Type guard for mypy
                continue

            dept_summary: DepartmentPayoutSummary = {
                "employees": [],
                "total_hours": 0,
                "total_payout": Decimal(0),  # Store as Decimal for sum
            }

            current_dept_total_hours = 0
            current_dept_total_payout = Decimal(0)

            # Sort employees by name within the department for consistent output
            sorted_employees = sorted(employees_in_dept, key=lambda e: e.name)

            for emp_record in sorted_employees:
                payout = emp_record.hours_worked * emp_record.hourly_rate
                dept_summary["employees"].append(
                    EmployeePayoutDetail(
                        name=emp_record.name,
                        hours=emp_record.hours_worked,
                        # Rate and payout will be string formatted by the formatter
                        # Here, we store them in a way the formatter can use
                        rate=str(emp_record.hourly_rate.quantize(Decimal("0.01"))),
                        payout=str(payout.quantize(Decimal("0.01"))),
                    )
                )
                current_dept_total_hours += emp_record.hours_worked
                current_dept_total_payout += payout

            dept_summary["total_hours"] = current_dept_total_hours

            dept_summary["total_payout"] = str(
                current_dept_total_payout.quantize(Decimal("0.01"))
            )

            processed_report[dept_name] = dept_summary

        sorted_processed_report = dict(sorted(processed_report.items()))

        return sorted_processed_report


class PayoutConsoleFormatter(ReportFormatterStrategy[PayoutReportData]):
    """Formats the payout report data for console output."""

    def _get_column_widths(self, report_data: PayoutReportData) -> Dict[str, int]:
        """Calculates maximum widths for each column for alignment."""
        # Add fixed prefix to names for width calculation
        name_prefix = "---------------- "
        max_name_len = len("Name")  # Header
        max_hours_len = len("Hours")
        max_rate_len = len("Rate")
        max_payout_len = len("Payout")

        for dept_summary in report_data.values():
            for emp in dept_summary["employees"]:
                max_name_len = max(max_name_len, len(name_prefix + emp["name"]))
                max_hours_len = max(max_hours_len, len(str(emp["hours"])))
                max_rate_len = max(max_rate_len, len(str(emp["rate"])))
                # Add 1 for '$' and potentially commas for larger numbers if needed
                max_payout_len = max(max_payout_len, len(f"${emp['payout']}"))

            max_hours_len = max(max_hours_len, len(str(dept_summary["total_hours"])))
            max_payout_len = max(
                max_payout_len, len(f"${dept_summary['total_payout']}")
            )

        # Ensure minimum width for headers if data is very narrow
        max_name_len = max(max_name_len, len(name_prefix + "Employee Name Sample"))
        max_hours_len = max(max_hours_len, 5)  # "Hours"
        max_rate_len = max(max_rate_len, 5)  # "Rate"
        max_payout_len = max(max_payout_len, 8)  # "$Payout"

        return {
            "name": max_name_len,
            "hours": max_hours_len,
            "rate": max_rate_len,
            "payout": max_payout_len,
        }

    def format(self, report_data: PayoutReportData) -> str:
        """
        Formats the payout report into a string suitable for console display.

        Args:
            report_data: The processed payout report data.

        Returns:
            A string containing the formatted report.
        """
        if not report_data:
            return "No data available to generate the report."

        output_lines: List[str] = []
        widths = self._get_column_widths(report_data)
        name_w, hours_w, rate_w, payout_w = (
            widths["name"],
            widths["hours"],
            widths["rate"],
            widths["payout"],
        )

        name_prefix = "---------------- "

        for dept_name, dept_summary in report_data.items():
            output_lines.append(f"\n{dept_name}")  # Department name
            for emp in dept_summary["employees"]:
                payout_str = f"${Decimal(emp['payout']):.0f}"
                rate_str = f"{Decimal(emp['rate']):.0f}"

                # Add prefix to name for display
                display_name = name_prefix + emp["name"]
                output_lines.append(
                    f"{display_name:<{name_w}} "
                    f"{emp['hours']:>{hours_w}} "
                    f"{rate_str:>{rate_w}} "
                    f"{payout_str:>{payout_w}}"
                )

            # Department totals
            total_payout_str = f"${Decimal(dept_summary['total_payout']):.0f}"
            output_lines.append(
                f"{'':<{name_w}} "  # Empty name column for total
                f"{dept_summary['total_hours']:>{hours_w}} "
                f"{'':>{rate_w}} "  # Empty rate column for total
                f"{total_payout_str:>{payout_w}}"
            )

        return "\n".join(output_lines).strip()
