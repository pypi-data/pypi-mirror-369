"""Main CLI entry point for SSF Tools."""

import rich_click as click
from rich.console import Console

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True

console = Console()


@click.group(
    name="ssf_tools",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(version="0.1.0", prog_name="SSF Tools")
def cli() -> None:
    """
    SSF Tools - Forensic Analysis Toolkit for cybersecurity professionals.

    A comprehensive toolkit for forensic analysis workflows including
    memory analysis with Volatility, SSL/TLS testing, and more.
    """


# Late import to avoid circular dependency
def register_commands() -> None:
    """Register all sub-commands."""
    from kp_ssf_tools.cli.commands.volatility import volatility

    cli.add_command(volatility)


# Register commands when module is imported
register_commands()


if __name__ == "__main__":
    cli()


if __name__ == "__main__":
    cli()
