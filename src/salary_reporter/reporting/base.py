"""Base classes for report generation and formatting strategies."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class ReportGeneratorStrategy(ABC, Generic[InputType, OutputType]):
    """
    Abstract base class for report generation strategies.

    A report generator takes a list of employee data and processes it
    into a structured format suitable for a specific report type.
    """

    @abstractmethod
    def generate(self, data: InputType) -> OutputType:
        """
        Generates a report from the given employee data.

        Args:
            data: The input data, typically a list of EmployeeData objects.

        Returns:
            The processed report data in a structured format.
        """
        pass


class ReportFormatterStrategy(ABC, Generic[InputType]):
    """
    Abstract base class for report formatting strategies.

    A report formatter takes processed report data and converts it
    into a final string representation (e.g., for console output, JSON).
    """

    @abstractmethod
    def format(self, report_data: InputType) -> str:
        """
        Formats the processed report data into a string.

        Args:
            report_data: The structured report data to format.

        Returns:
            A string representation of the report.
        """
        pass
