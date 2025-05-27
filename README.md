
# Salary Reporter

A Python script designed to calculate employee salaries from CSV data files and generate insightful reports. This tool processes employee records, including hours worked and hourly rates, to produce various reports, with an initial focus on a detailed payout summary.

## Key Features

*   **Flexible Data Ingestion:** Reads employee data from one or more CSV files.
*   **Smart Column Recognition:** Handles variations in CSV column names for critical data like hourly rate (e.g., `hourly_rate`, `rate`, `salary`) and hours worked (e.g., `hours_worked`, `hours`).
*   **Payout Reporting:** Generates a clear, console-based payout report, conveniently grouped by department.
*   **Modular Architecture:** Built with extensibility in mind, allowing for straightforward addition of new report types or output formats.
*   **User-Friendly CLI:** Offers a command-line interface powered by Python's `argparse` module.
*   **Clean Codebase:** Features type-annotated code with comprehensive Google-style docstrings.
*   **Robust Testing:** Includes a thorough test suite using `pytest`, ensuring reliability.
*   **Best Practices:** Adheres to standard Python styling, linted with `ruff`, and avoids external libraries like `csv` or `pandas` for core CSV processing, per specific project constraints.

## Project Structure

The project is organized as follows:

```
salary_calculator_project/
├── src/
│   └── salary_reporter/      # Main application Python package
│       ├── __init__.py
│       ├── cli.py            # Command-Line Interface logic
│       ├── config.py         # Application configuration (e.g., column name variants)
│       ├── custom_types.py   # Custom type aliases for clarity
│       ├── data_loader.py    # CSV data loading and parsing engine
│       ├── domain_models.py  # Core data structures (e.g., EmployeeData)
│       ├── exceptions.py     # Custom exception classes
│       ├── main.py           # Main script entry point for the package
│       └── reporting/        # Subsystem for report generation and formatting
│           ├── __init__.py
│           ├── base.py       # Abstract base classes for report strategies
│           ├── payout_report.py # Logic specific to the payout report
│           └── registry.py   # Registry for available report types
├── tests/                    # Unit and integration tests
│   ├── data/                 # Sample CSV files for testing
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures and shared test configurations
│   ├── test_cli.py
│   ├── test_data_loader.py
│   └── test_reporting/
│       ├── __init__.py
│       ├── test_payout_report.py
│       └── test_registry.py
├── .gitignore                # Specifies intentionally untracked files
├── pyproject.toml            # Project metadata and dependencies (Poetry)
└── README.md                 # This file```
```
## Setup and Installation

This project utilizes [Poetry](https://python-poetry.org/) for robust dependency management and packaging.

1.  **Prerequisites:**
    *   Python (version 3.9 or newer recommended).
    *   Poetry (refer to [Poetry's official documentation](https://python-poetry.org/docs/#installation) for installation instructions if you don't have it).

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/fluffy-dev/salary_calculator_project.git
    cd salary_calculator_project
    ```

3.  **Install Project Dependencies:**
    Poetry will create a virtual environment and install all necessary packages.
    ```bash
    poetry install
    ```

4.  **Using the Virtual Environment:**
    Commands should typically be run using `poetry run <command>` to ensure they execute within the project's isolated environment.

    Alternatively, if you prefer to activate the virtual environment for your current shell session:
    *   Find the environment's path:
        ```bash
        poetry env info --path
        ```
    *   Activate it (example for bash/zsh):
        ```bash
        source $(poetry env info --path)/bin/activate
        ```
    If you install the `poetry-plugin-shell` (`poetry self add poetry-plugin-shell`), you can use the traditional `poetry shell` command.

## Usage

Execute the script via the command line, providing paths to your CSV data files.

**Command Syntax:**

```bash
poetry run salary-report [CSV_FILE_PATHS...] --report [REPORT_TYPE]
```
If you have a root `main.py` script configured as an alternative entry point:
```bash
python main.py [CSV_FILE_PATHS...] --report [REPORT_TYPE]
```

**Example:**

To generate a `payout` report using data from `employees_normal.csv` and `employees_rate_col.csv` (assuming these files are in a `data/` subdirectory):

```bash
poetry run salary-report tests/data/employees_normal.csv tests/data/employees_rate_col.csv --report payout
```

**Input CSV File Format:**

*   Files must include a header row.
*   Expected columns are generally `id, email, name, department, hours_worked, hourly_rate`.
*   The script intelligently recognizes common variations:
    *   `hourly_rate` can also be `rate` or `salary`.
    *   `hours_worked` can also be `hours`.
*   The order of columns in the CSV file does not matter.
*   The parser assumes a simple CSV structure where commas are exclusively delimiters (i.e., no commas within data fields, even if quoted).

**Example `payout` Report Output:**

Run this:
```bash 
poetry run salary-report tests/data/employees_normal.csv --report payout
```

Output will be this:
```
Design
---------------- Bob Smith                  150       40    $6000
---------------- Carol Williams             170       60   $10200
                                           320            $16200
Marketing
---------------- Alice Johnson              160       50    $8000
                                           160             $8000
```

## Development Workflow

### Linting and Formatting

This project employs `ruff` for efficient linting and code formatting to maintain consistency and quality.

*   **Check for linting issues:**
    ```bash
    poetry run ruff check .
    ```
*   **Automatically format code:**
    ```bash
    poetry run ruff format .
    ```

### Running Tests and Checking Coverage

The test suite is built with `pytest`.

*   **Execute all tests:**
    ```bash
    poetry run pytest
    ```
*   **Run tests and generate a coverage report:**
    ```bash
    poetry run pytest --cov=salary_reporter --cov-report=term-missing --cov-report=html
    ```
    After execution, the detailed HTML coverage report can be found at `htmlcov/index.html`. The project aims to sustain a test coverage level above 80%.

## Extending the Application

The application's architecture is designed for modularity, simplifying the addition of new functionalities.

### Adding a New Report Type

To introduce a new type of report (e.g., "average hourly rate by department"):

1.  **Develop a Report Generator:**
    *   Inside `src/salary_reporter/reporting/`, create a new Python file (e.g., `average_rate_report.py`).
    *   Define a class inheriting from `ReportGeneratorStrategy` (from `src.salary_reporter.reporting.base`).
    *   Implement the `generate(self, data: EmployeeDataList) -> ProcessedReportData` method. This method will take the list of `EmployeeData` objects and transform it into a Python dictionary or list (`ProcessedReportData`) specific to your new report's needs.

    *Example:*
    ```python
    # src/salary_reporter/reporting/average_rate_report.py
    from salary_reporter.custom_types import EmployeeDataList, ProcessedReportData
    from salary_reporter.reporting.base import ReportGeneratorStrategy

    class AverageRateReportGenerator(ReportGeneratorStrategy[EmployeeDataList, ProcessedReportData]):
        def generate(self, data: EmployeeDataList) -> ProcessedReportData:
            # ... your logic to calculate average rates ...
            report_content = {"department_averages": {}} # Populate this
            return report_content
    ```

2.  **Develop a Report Formatter:**
    *   In the same file (or a related one), define a class inheriting from `ReportFormatterStrategy`.
    *   Implement the `format(self, report_data: ProcessedReportData) -> str` method. This takes the structured data from your generator and converts it into the desired string output (e.g., console text, JSON).

    *Example:*
    ```python
    # src/salary_reporter/reporting/average_rate_report.py (continued)
    from salary_reporter.reporting.base import ReportFormatterStrategy

    class AverageRateConsoleFormatter(ReportFormatterStrategy[ProcessedReportData]):
        def format(self, report_data: ProcessedReportData) -> str:
            # ... your logic to format the average rate data for console ...
            return "Formatted average rate report..."
    ```

3.  **Register the New Report:**
    *   Edit `src/salary_reporter/reporting/registry.py`.
    *   Import your newly created generator and formatter classes.
    *   Add an entry to the `_REPORT_REGISTRY` dictionary. The key becomes the identifier for the `--report` CLI argument.

    *Example:*
    ```python
    # src/salary_reporter/reporting/registry.py
    # ... other imports
    from .average_rate_report import (
        AverageRateReportGenerator,
        AverageRateConsoleFormatter,
    )

    _REPORT_REGISTRY: Dict[str, ReportConfiguration] = {
        "payout": ReportConfiguration(PayoutReportGenerator, PayoutConsoleFormatter),
        "average_rate": ReportConfiguration( # This is your new report's CLI name
            AverageRateReportGenerator, AverageRateConsoleFormatter
        ),
    }
    ```

4.  **Update CLI (Usually Not Required):**
    The `cli.py` module dynamically populates the `--report` argument's choices from the registry. Manual CLI changes are typically only needed if your new report requires unique command-line arguments.

5.  **Write Comprehensive Tests:**
    *   Add new test files within `tests/test_reporting/` to cover your new generator and formatter. Strive for thorough test coverage.

### Adding a New Output Format for an Existing Report

To support additional output formats (e.g., JSON) for an existing report type:

1.  **Create a New Formatter Class:** For instance, `PayoutJSONFormatter` in `payout_report.py`, inheriting from `ReportFormatterStrategy`.
    ```python
    # src/salary_reporter/reporting/payout_report.py
    import json
    # ...
    class PayoutJSONFormatter(ReportFormatterStrategy[PayoutReportData]):
        def format(self, report_data: PayoutReportData) -> str:
            return json.dumps(report_data, indent=2)
    ```
2.  **Adapt CLI and Registry:** This would involve modifying `cli.py` to accept an `--output-format` argument and potentially adjusting `registry.py` or the `ReportConfiguration` class to manage multiple formatters per report type. This is a more involved change, as the current design prioritizes ease of adding new *report types*. A simpler approach for a single new output format might involve a dedicated CLI flag handled directly in `cli.py` to select the alternative formatter for a specific report.
