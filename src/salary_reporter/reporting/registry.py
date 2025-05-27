"""Registry for report generators and formatters."""

from typing import Dict, List, Type

from salary_reporter.exceptions import UnsupportedReportTypeError
from salary_reporter.reporting.base import (
    ReportFormatterStrategy,
    ReportGeneratorStrategy,
)
from salary_reporter.reporting.payout_report import (
    PayoutConsoleFormatter,
    PayoutReportGenerator,
)


class ReportConfiguration:
    """Holds the generator and formatter for a specific report type."""

    def __init__(
        self,
        generator_cls: Type[ReportGeneratorStrategy],
        formatter_cls: Type[ReportFormatterStrategy],
    ) -> None:
        """
        Initializes a report configuration.

        Args:
            generator_cls: The class for generating the report data.
            formatter_cls: The class for formatting the report data.
        """
        self.generator_cls = generator_cls
        self.formatter_cls = formatter_cls


_REPORT_REGISTRY: Dict[str, ReportConfiguration] = {
    "payout": ReportConfiguration(PayoutReportGenerator, PayoutConsoleFormatter),
    # New report types can be added here
    # "average_rate":
    #       ReportConfiguration(
    #         AverageRateGenerator,
    #         AverageRateConsoleFormatter
    #       ),
}


def get_report_configuration(report_name: str) -> ReportConfiguration:
    """
    Retrieves the report generator and formatter classes for a given report name.

    Args:
        report_name: The name of the report type (e.g., "payout").

    Returns:
        A ReportConfiguration object containing the generator and formatter classes.

    Raises:
        UnsupportedReportTypeError: If the report_name is not registered.
    """
    report_name_lower = report_name.lower()
    if report_name_lower not in _REPORT_REGISTRY:
        raise UnsupportedReportTypeError(
            f"Report type '{report_name}' is not supported. "
            f"Available types: {', '.join(_REPORT_REGISTRY.keys())}"
        )
    return _REPORT_REGISTRY[report_name_lower]


def get_available_reports() -> List[str]:
    """Returns a list of available report names."""
    return list(_REPORT_REGISTRY.keys())
