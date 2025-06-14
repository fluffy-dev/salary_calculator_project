"""Custom type aliases used across the application."""

from typing import Any, Dict, List, TypedDict

from salary_reporter.domain_models import EmployeeData


class EmployeePayoutDetail(TypedDict):
    """Structure for individual employee payout details in a report."""

    name: str
    hours: int
    rate: str  # Formatted rate
    payout: str  # Formatted payout


class DepartmentPayoutSummary(TypedDict):
    """Structure for department-level payout summaries."""

    employees: List[EmployeePayoutDetail]
    total_hours: int
    total_payout: str  # Formatted total payout


# Defines the structure of the raw data generated by PayoutReportGenerator
PayoutReportData = Dict[str, DepartmentPayoutSummary]

# General type for any processed report data before formatting
ProcessedReportData = Dict[str, Any]

# Type for a list of EmployeeData objects
EmployeeDataList = List[EmployeeData]
