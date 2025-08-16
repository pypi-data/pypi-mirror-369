"""Rich console styling helpers for SSF Tools."""

from rich.console import Console
from rich.theme import Theme

# Custom theme for SSF Tools
SSF_THEME = Theme(
    {
        "error": "bold red",
        "warning": "bold yellow",
        "success": "bold green",
        "info": "bold blue",
        "highlight": "bold cyan",
        "path": "bold magenta",
        "command": "bold white on black",
    },
)

# Global console instance with custom theme
console = Console(theme=SSF_THEME)


def print_error(message: str) -> None:
    """Print an error message with consistent styling."""
    console.print(f"[error]Error:[/error] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with consistent styling."""
    console.print(f"[warning]Warning:[/warning] {message}")


def print_success(message: str) -> None:
    """Print a success message with consistent styling."""
    console.print(f"[success]Success:[/success] {message}")


def print_info(message: str) -> None:
    """Print an info message with consistent styling."""
    console.print(f"[info]Info:[/info] {message}")


def print_highlight(message: str) -> None:
    """Print a highlighted message."""
    console.print(f"[highlight]{message}[/highlight]")


def print_path(path: str) -> None:
    """Print a file path with consistent styling."""
    console.print(f"[path]{path}[/path]")


def print_command(command: str) -> None:
    """Print a command with consistent styling."""
    console.print(f"[command]{command}[/command]")
