"""Pytest fixtures and configuration."""

from decimal import Decimal
from pathlib import Path
from typing import Callable, List

import pytest

from salary_reporter.domain_models import EmployeeData


@pytest.fixture()
def sample_employee_data_list() -> List[EmployeeData]:
    """Provides a sample list of EmployeeData objects."""
    return [
        EmployeeData(
            "1", "alice@example.com", "Alice Johnson", "Marketing", 160, Decimal("50")
        ),
        EmployeeData("2", "bob@example.com", "Bob Smith", "Design", 150, Decimal("40")),
        EmployeeData(
            "3", "carol@example.com", "Carol Williams", "Design", 170, Decimal("60")
        ),
    ]


@pytest.fixture()
def temp_csv_file(tmp_path: Path) -> Callable[[str, str], Path]:
    """
    Factory fixture to create a temporary CSV file.

    Args:
        tmp_path: Pytest fixture for a temporary directory path.

    Returns:
        A function that takes content and an optional filename,
        creates the file in tmp_path, and returns its Path object.
    """

    def _create_temp_csv(content: str, filename: str = "temp.csv") -> Path:
        """
        Creates a temporary CSV file with the given content and name.

        Args:
            content: The string content to write to the file.
            filename: The name for the temporary file.

        Returns:
            The Path object of the created file.
        """
        file_path = tmp_path / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_temp_csv
