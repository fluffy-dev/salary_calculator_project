"""Main entry point for the salary reporter application."""

from salary_reporter.cli import run as run_cli_app


def run_cli() -> None:
    """
    Executes the command-line interface of the salary reporter.

    This function is intended to be used as the entry point for the
    script defined in pyproject.toml.
    """
    run_cli_app()


if __name__ == "__main__":
    run_cli()
