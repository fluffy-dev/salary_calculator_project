"""Domain models for the salary reporter."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class EmployeeData:
    """
    Represents a single employee's data record.

    Attributes:
        employee_id: The unique identifier for the employee.
        email: The employee's email address.
        name: The employee's full name.
        department: The department the employee belongs to.
        hours_worked: The number of hours worked by the employee.
        hourly_rate: The employee's hourly rate.
    """

    employee_id: str
    email: str
    name: str
    department: str
    hours_worked: int
    hourly_rate: Decimal  # Using Decimal for financial precision
