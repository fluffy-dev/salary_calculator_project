"""Custom exceptions for the salary reporter application."""


class SalaryReporterError(Exception):
    """Base exception for this application."""

    pass


class DataLoaderError(SalaryReporterError):
    """Exception related to data loading or parsing."""

    pass


class MissingHeaderError(DataLoaderError):
    """Exception raised when a CSV file is missing a header row."""

    pass


class MissingColumnError(DataLoaderError):
    """Exception raised when a required column is missing in the CSV header."""

    pass


class DataParsingError(DataLoaderError):
    """Exception raised when data within a row cannot be parsed correctly."""

    pass


class ReportGenerationError(SalaryReporterError):
    """Exception related to report generation."""

    pass


class UnsupportedReportTypeError(SalaryReporterError):
    """Exception for when an unsupported report type is requested."""

    pass
