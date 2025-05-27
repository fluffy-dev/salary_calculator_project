"""Tests for the CSVDataLoader."""

from decimal import Decimal
from pathlib import Path
from typing import Callable

import pytest

from salary_reporter.data_loader import CSVDataLoader
from salary_reporter.domain_models import EmployeeData
from salary_reporter.exceptions import (
    DataLoaderError,
    DataParsingError,
    MissingColumnError,
    MissingHeaderError,
)

TempCsvFileFixture = Callable[[str, str], Path]


@pytest.fixture()
def loader() -> CSVDataLoader:
    """Fixture for CSVDataLoader instance."""
    return CSVDataLoader()


def test_load_normal_csv(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading a standard CSV file."""
    content = (
        "id,email,name,department,hours_worked,hourly_rate\n"
        "1,alice@example.com,Alice Johnson,Marketing,160,50\n"
        "2,bob@example.com,Bob Smith,Design,150,40"
    )
    file_path = temp_csv_file(content, "normal.csv")
    data = loader.load_data_from_file(str(file_path))

    assert len(data) == 2
    assert data[0] == EmployeeData(
        "1", "alice@example.com", "Alice Johnson", "Marketing", 160, Decimal("50")
    )
    assert data[1] == EmployeeData(
        "2", "bob@example.com", "Bob Smith", "Design", 150, Decimal("40")
    )


def test_load_csv_with_rate_column(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading CSV with 'rate' as hourly rate column."""
    content = (
        "id,name,department,hours_worked,rate,email\n"
        "1,Dave Davis,Sales,100,55,dave@example.com"
    )
    file_path = temp_csv_file(content, "rate_col.csv")
    data = loader.load_data_from_file(str(file_path))
    assert len(data) == 1
    assert data[0].hourly_rate == Decimal("55")
    assert data[0].name == "Dave Davis"  # Check other fields map correctly


def test_load_csv_with_salary_column(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading CSV with 'salary' as hourly rate column."""
    content = (
        "id,name,department,hours,salary,email\n"
        "1,Eve Evans,HR,120,45,eve@example.com"
    )  # 'hours' also a variant
    file_path = temp_csv_file(content, "salary_col.csv")
    data = loader.load_data_from_file(str(file_path))
    assert len(data) == 1
    assert data[0].hourly_rate == Decimal("45")
    assert data[0].hours_worked == 120


def test_load_empty_file(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading an empty file."""
    file_path = temp_csv_file("", "empty.csv")
    with pytest.raises(MissingHeaderError, match="empty or has no header"):
        loader.load_data_from_file(str(file_path))


def test_load_file_only_header(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading a file with only a header row."""
    content = "id,name,department,hours_worked,hourly_rate,email"
    file_path = temp_csv_file(content, "header_only.csv")
    data = loader.load_data_from_file(str(file_path))
    assert len(data) == 0


def test_load_missing_required_column(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading CSV missing a critical column (e.g., name)."""
    content = "id,department,hours_worked,hourly_rate\n" "1,Tech,100,20"
    file_path = temp_csv_file(content, "missing_col.csv")
    with pytest.raises(
        MissingColumnError, match="Required column for 'email'"
    ):  # or 'name'
        loader.load_data_from_file(str(file_path))


def test_load_no_valid_rate_column(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading CSV without any recognizable hourly rate column."""
    content = "id,name,department,hours_worked,wage,email"  # Added email
    file_path = temp_csv_file(content, "no_rate_col.csv")
    with pytest.raises(MissingColumnError, match="Required column for 'hourly_rate'"):
        loader.load_data_from_file(str(file_path))


def test_load_malformed_data_non_numeric(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test CSV with non-numeric data where numbers are expected."""
    content_hours = (
        "id,name,department,hours_worked,hourly_rate,email\n"
        "1,Bad Data,Test,one hundred,50,bad@example.com"
    )
    file_path_hours = temp_csv_file(content_hours, "malformed_hours.csv")

    with pytest.raises(
        DataParsingError, match=r"Error parsing data.*invalid literal for int\(\) with base 10: 'one hundred'"
    ):
        loader.load_data_from_file(str(file_path_hours))

    content_rate = (
        "id,name,department,hours_worked,hourly_rate,email\n"
        "2,Bad Rate,Test,100,fifty,badrate@example.com"
    )
    file_path_rate = temp_csv_file(content_rate, "malformed_rate.csv")

    with pytest.raises(
        DataParsingError, match=r"Error parsing data.*\[<class 'decimal.ConversionSyntax'>\]"
    ):
        loader.load_data_from_file(str(file_path_rate))


def test_load_negative_values(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test CSV with negative hours or rate."""
    content = (
        "id,name,department,hours_worked,hourly_rate,email\n"
        "1,Neg Hours,Test,-10,50,neg@example.com"
    )
    file_path = temp_csv_file(content, "neg_hours.csv")
    with pytest.raises(
        DataParsingError, match="Hours worked and hourly rate cannot be negative"
    ):
        loader.load_data_from_file(str(file_path))

    content_rate = (
        "id,name,department,hours_worked,hourly_rate,email\n"
        "2,Neg Rate,Test,100,-50,negrate@example.com"
    )
    file_path_rate = temp_csv_file(content_rate, "neg_rate.csv")
    with pytest.raises(
        DataParsingError, match="Hours worked and hourly rate cannot be negative"
    ):
        loader.load_data_from_file(str(file_path_rate))


def test_load_all_data_multiple_files(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test loading data from multiple CSV files."""
    content1 = \
        "id,name,department,hours_worked,hourly_rate,email\n1,Alice,Dev,10,1,a@e.c"

    content2 = \
        "id,name,department,hours,rate,email\n2,Bob,QA,20,2,b@e.c"

    file1 = temp_csv_file(content1, "file1.csv")
    file2 = temp_csv_file(content2, "file2.csv")

    all_data = loader.load_all_data([str(file1), str(file2)])
    assert len(all_data) == 2
    assert all_data[0].name == "Alice"
    assert all_data[1].name == "Bob"
    assert all_data[0].hourly_rate == Decimal("1")
    assert all_data[1].hourly_rate == Decimal("2")


def test_file_not_found(loader: CSVDataLoader) -> None:
    """Test loading a non-existent file."""
    with pytest.raises(DataLoaderError, match="File not found"):
        loader.load_data_from_file("non_existent_file.csv")


def test_skip_empty_lines(
    loader: CSVDataLoader, temp_csv_file: TempCsvFileFixture
) -> None:
    """Test that empty lines in data are skipped."""
    content = (
        "id,email,name,department,hours_worked,hourly_rate\n"
        "1,alice@example.com,Alice Johnson,Marketing,160,50\n"
        "\n"  # Empty line
        "2,bob@example.com,Bob Smith,Design,150,40\n"
    )
    file_path = temp_csv_file(content, "empty_lines.csv")
    data = loader.load_data_from_file(str(file_path))
    assert len(data) == 2
