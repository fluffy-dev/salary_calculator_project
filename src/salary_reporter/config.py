"""Configuration constants for the salary reporter."""

from typing import Tuple

POSSIBLE_ID_COLUMNS: Tuple[str, ...] = ("id",)
POSSIBLE_EMAIL_COLUMNS: Tuple[str, ...] = ("email",)
POSSIBLE_NAME_COLUMNS: Tuple[str, ...] = ("name", "employee_name")
POSSIBLE_DEPARTMENT_COLUMNS: Tuple[str, ...] = ("department", "dept")
POSSIBLE_HOURS_WORKED_COLUMNS: Tuple[str, ...] = ("hours_worked", "hours")
POSSIBLE_HOURLY_RATE_COLUMNS: Tuple[str, ...] = (
    "hourly_rate",
    "rate",
    "salary",
)

EXPECTED_COLUMNS: int = 6 # id,email,name,department,hours_worked,hourly_rate