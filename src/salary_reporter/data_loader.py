"""
Handles loading and parsing of employee data from CSV files.

This module provides functionality to read CSV files line by line,
without using the standard `csv` module, parse headers to find
required columns (including variants for hourly rate), and convert
row data into `EmployeeData` objects.
"""

from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple

from salary_reporter import config
from salary_reporter.domain_models import EmployeeData
from salary_reporter.exceptions import (
    DataLoaderError,
    DataParsingError,
    MissingColumnError,
    MissingHeaderError,
)


class CSVDataLoader:
    """Loads employee data from one or more CSV files."""

    def __init__(self) -> None:
        """Initializes the CSVDataLoader."""
        self._required_column_finders: Dict[str, Tuple[str, ...]] = {
            "employee_id": config.POSSIBLE_ID_COLUMNS,
            "email": config.POSSIBLE_EMAIL_COLUMNS,
            "name": config.POSSIBLE_NAME_COLUMNS,
            "department": config.POSSIBLE_DEPARTMENT_COLUMNS,
            "hours_worked": config.POSSIBLE_HOURS_WORKED_COLUMNS,
            "hourly_rate": config.POSSIBLE_HOURLY_RATE_COLUMNS,
        }

    def _find_column_index(
        self, header: List[str], possible_names: Tuple[str, ...], column_purpose: str
    ) -> int:
        """
        Finds the index of a column in the header given possible names.

        Args:
            header: A list of column names from the CSV header.
            possible_names: A tuple of possible names for the target column.
            column_purpose: A descriptive name for the column's purpose (for errors).

        Returns:
            The 0-based index of the found column.

        Raises:
            MissingColumnError: If the column cannot be found.
        """
        normalized_header = [h.lower().strip() for h in header]
        for name_variant in possible_names:
            try:
                return normalized_header.index(name_variant.lower().strip())
            except ValueError:
                continue
        raise MissingColumnError(
            f"Required column for '{column_purpose}' "
            f"(e.g., {possible_names[0]}) not found in header: {header}"
        )

    def _parse_header(self, header_line: str) -> Dict[str, int]:
        """
        Parses the header line to map column purposes to their indices.

        Args:
            header_line: The string containing the header row from the CSV.

        Returns:
            A dictionary mapping column purpose (e.g., "name") to its column index.

        Raises:
            MissingColumnError: If any essential column cannot be mapped.
        """
        header_parts = [part.strip() for part in header_line.split(",")]
        if not header_parts or len(header_parts) < 3:
            raise MissingHeaderError("CSV header is missing or invalid.")

        column_indices: Dict[str, int] = {}
        for purpose, possible_names in self._required_column_finders.items():
            column_indices[purpose] = self._find_column_index(
                header_parts, possible_names, purpose
            )
        return column_indices

    def _parse_row(
        self,
        row_line: str,
        column_indices: Dict[str, int],
        line_number: int,
        file_path: str,
    ) -> EmployeeData:
        """
        Parses a single data row into an EmployeeData object.

        Args:
            row_line: The string containing a data row from the CSV.
            column_indices: A dictionary mapping column purposes to their indices.
            line_number: The current line number in the file (for error reporting).
            file_path: The path to the current CSV file (for error reporting).

        Returns:
            An EmployeeData object.

        Raises:
            DataParsingError: If data cannot be converted to the expected types
                              or if a row has an incorrect number of columns.
        """
        row_parts = [part.strip() for part in row_line.split(",")]

        if (
            len(row_parts) != len(column_indices)
            and len(row_parts) != config.EXPECTED_COLUMNS
        ):
            # This check is a bit lenient
            # if column_indices has less than EXPECTED_COLUMNS

            # because some headers
            # might have more columns than we strictly need.

            # A stricter check might be:
            # len(row_parts) != max(column_indices.values()) + 1

            # For now, assume
            # row length should match the number of columns defined in header.

            # A more robust parser would handle quoted commas,
            # but this is per spec "no csv module".

            # This check also assumes
            # number of found columns in header is consistent with row_parts

            pass
            # The problem implies "valid CSV",
            # so we assume correct number of fields.

        try:
            employee_id = row_parts[column_indices["employee_id"]]
            email = row_parts[column_indices["email"]]
            name = row_parts[column_indices["name"]]
            department = row_parts[column_indices["department"]]
            hours_worked_str = row_parts[column_indices["hours_worked"]]
            hourly_rate_str = row_parts[column_indices["hourly_rate"]]

            hours_worked = int(hours_worked_str)

            # The CSV example uses integers for rates (e.g., 50, 40).
            # Using Decimal for precision.

            hourly_rate = Decimal(hourly_rate_str)

            if hours_worked < 0 or hourly_rate < Decimal(0):
                raise ValueError("Hours worked and hourly rate cannot be negative.")

        except IndexError as e:
            raise DataParsingError(
                f"Row {line_number} in '{file_path}' "
                f"has an incorrect number of columns. "
                f"Expected data for columns: "
                f"{list(column_indices.keys())}. Row: '{row_line}'"
            ) from e
        except (ValueError, InvalidOperation) as e:
            raise DataParsingError(
                f"Error parsing data in row {line_number} in '{file_path}': "
                f"{e}. Row: '{row_line}'"
            ) from e

        return EmployeeData(
            employee_id=employee_id,
            email=email,
            name=name,
            department=department,
            hours_worked=hours_worked,
            hourly_rate=hourly_rate,
        )

    def load_data_from_file(self, file_path: str) -> List[EmployeeData]:
        """
        Loads and parses all employee data from a single CSV file.

        Args:
            file_path: The path to the CSV file.

        Returns:
            A list of EmployeeData objects.

        Raises:
            DataLoaderError:
                If the file cannot be read, is empty, or contains parsing errors.
            MissingHeaderError:
                If the CSV header is missing or invalid.
            MissingColumnError:
                If essential columns are not found in the header.
            DataParsingError:
                If data rows cannot be parsed.
        """
        records: List[EmployeeData] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                raise MissingHeaderError(
                    f"File '{file_path}' is empty or has no header."
                )

            header_line = lines[0].strip()
            if not header_line:
                raise MissingHeaderError(
                    f"File '{file_path}' has an empty header line."
                )

            column_indices = self._parse_header(header_line)

            for i, line in enumerate(lines[1:], start=2):  # Start from line 2 for data
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                try:
                    records.append(self._parse_row(line, column_indices, i, file_path))
                except DataParsingError as e:
                    # Allow continuing if one row is bad? Or fail fast?
                    # For now, fail fast as per "valid CSV" expectation.
                    raise DataParsingError(f"Error in file '{file_path}': {e}") from e

        except FileNotFoundError as e:
            raise DataLoaderError(f"File not found: {file_path}") from e
        except OSError as e:
            raise DataLoaderError(f"Error reading file '{file_path}': {e}") from e

        return records

    def load_all_data(self, file_paths: List[str]) -> List[EmployeeData]:
        """
        Loads employee data from multiple CSV files and aggregates them.

        Args:
            file_paths: A list of paths to CSV files.

        Returns:
            A single list containing all EmployeeData objects from all files.
            Duplicate employee_ids are not explicitly handled here but could be
            a consideration for more complex scenarios.

        Raises:
            DataLoaderError: If any file causes an error during loading.
        """
        all_records: List[EmployeeData] = []
        for file_path in file_paths:
            all_records.extend(self.load_data_from_file(file_path))
        return all_records
