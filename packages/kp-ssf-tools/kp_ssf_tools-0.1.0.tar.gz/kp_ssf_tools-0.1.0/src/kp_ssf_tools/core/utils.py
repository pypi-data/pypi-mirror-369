"""Common utilities shared across SSF Tools."""

import platform
import shutil
from pathlib import Path

from kp_ssf_tools.core.rich_helpers import console, print_error


def get_volatility_command() -> str:
    """Get the appropriate Volatility command based on the operating system."""
    if platform.system() == "Windows":
        return "vol.exe"
    return "vol"


def check_volatility_available() -> bool:
    """Check if Volatility command is available on the system PATH."""
    command = get_volatility_command()
    return shutil.which(command) is not None


def validate_volatility_installation() -> None:
    """Validate that Volatility is installed and available."""
    command = get_volatility_command()
    if not shutil.which(command):
        print_error(f"Volatility command '{command}' not found on PATH.")
        console.print(
            "Install Volatility with: [bold]pipx install volatility3[full][/bold]",
        )
        raise SystemExit(1)


def read_text_file_lines(file_path: Path) -> list[str]:
    """Read a text file and return lines, handling different line endings."""
    try:
        with file_path.open(encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with file_path.open(encoding="latin-1") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    else:
        return lines


def create_directory_safe(directory: Path) -> None:
    """Create a directory, creating parent directories as needed."""
    directory.mkdir(parents=True, exist_ok=True)


def handle_duplicate_process_names(
    process_matches: dict[str, list[int]],
) -> dict[str, int]:
    """Handle duplicate process names by appending numeric suffixes."""
    interesting_pids: dict[str, int] = {}

    for process_name, pids in process_matches.items():
        if len(pids) == 1:
            # Single instance, no suffix needed
            interesting_pids[process_name] = pids[0]
        else:
            # Multiple instances, add numeric suffixes
            for i, pid in enumerate(pids):
                if i == 0:
                    # First instance gets no suffix
                    interesting_pids[process_name] = pid
                else:
                    # Subsequent instances get _2, _3, etc.
                    interesting_pids[f"{process_name}_{i + 1}"] = pid

    return interesting_pids


def _find_pid_line_in_content(pid: int, pid_list_content: str) -> str | None:
    """Find the actual process line for a given PID in the content."""
    pid_lines = pid_list_content.split("\n")

    for line in pid_lines:
        if line.strip() and str(pid) in line and line.strip().startswith(str(pid)):
            return line.strip()

    return None


def _get_user_selection_for_conflict(
    pid: int,
    conflicting_targets: list[str],
    pid_line: str | None,
) -> str:
    """Present conflict to user and get their selection for resolution."""
    console.print("\n[yellow]PID Conflict Detected:[/yellow]")
    console.print(
        f"PID {pid} was matched by multiple target processes: {conflicting_targets}",
    )

    if pid_line:
        console.print("\n[cyan]Actual process in memory dump:[/cyan]")
        console.print(f"  {pid_line}")
        console.print()

    console.print(
        "[yellow]This PID should be assigned to which target process?[/yellow]",
    )
    console.print(
        "[dim](Choose the target that best matches the actual process name above)[/dim]",
    )

    # Display options
    for i, target in enumerate(conflicting_targets, 1):
        console.print(f"  {i}. [green]{target}[/green]")
    console.print(f"  {len(conflicting_targets) + 1}. [red]Cancel operation[/red]")

    # Get user selection
    while True:
        try:
            console.print(
                f"\nEnter your choice (1-{len(conflicting_targets) + 1}): ",
                end="",
            )
            choice = input().strip()

            if not choice:
                console.print("[red]Please enter a valid choice.[/red]")
                continue

            choice_num = int(choice)

            # Check if user wants to cancel
            if choice_num == len(conflicting_targets) + 1:
                console.print("[red]Operation cancelled by user[/red]")
                raise SystemExit(1) from None

            # Check if choice is valid
            if 1 <= choice_num <= len(conflicting_targets):
                selected_target = conflicting_targets[choice_num - 1]
                console.print(
                    f"[green]✓ Assigned PID {pid} to: {selected_target}[/green]",
                )
                return selected_target

            console.print(
                f"[red]Please enter a number between 1 and {len(conflicting_targets) + 1}.[/red]",
            )

        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")
        except KeyboardInterrupt:
            console.print("\n[red]Operation cancelled by user[/red]")
            raise SystemExit(1) from None


def resolve_pid_conflicts(
    process_matches: dict[str, list[int]],
    pid_list_content: str,
) -> tuple[dict[str, list[int]], list[str]]:
    """
    Resolve PID conflicts where the same PID is assigned to multiple target processes.

    Args:
        process_matches: Dictionary mapping target process names to lists of PIDs
        pid_list_content: Full content of the PID list file for line lookup

    Returns:
        Tuple of (cleaned process_matches dict, list of conflict resolution messages)

    """
    from collections import defaultdict

    # Build PID -> targets mapping
    pid_to_targets: dict[int, list[str]] = defaultdict(list)
    for target, pids in process_matches.items():
        for pid in pids:
            pid_to_targets[pid].append(target)

    # Find conflicts (PIDs that matched multiple targets)
    conflicts = {
        pid: targets for pid, targets in pid_to_targets.items() if len(targets) > 1
    }

    if not conflicts:
        return process_matches, []

    # Resolve conflicts
    resolved_matches = process_matches.copy()
    conflict_messages = []

    for pid, conflicting_targets in conflicts.items():
        # Find the actual line from the PID list for this PID
        pid_line = _find_pid_line_in_content(pid, pid_list_content)

        # Remove PID from all conflicting targets
        for target in conflicting_targets:
            resolved_matches[target] = [p for p in resolved_matches[target] if p != pid]

        # Get user selection for which target should receive this PID
        selected_target = _get_user_selection_for_conflict(
            pid,
            conflicting_targets,
            pid_line,
        )

        # Apply the user's resolution
        resolved_matches[selected_target].append(pid)

        # Log the resolution
        conflict_messages.append(
            f"PID {pid} conflict: {conflicting_targets} → assigned to '{selected_target}' (user selected)",
        )

    return resolved_matches, conflict_messages


def normalize_process_name(name: str) -> str:
    """Normalize process name for matching."""
    # Convert to lowercase for case-insensitive matching
    normalized = name.lower()

    # Define all possible extensions
    extensions = [".exe", ".com", ".bat", ".cmd", ".scr"]

    # First, check for complete extensions
    for ext in extensions:
        if normalized.endswith(ext):
            return normalized[: -len(ext)]

    # Handle partial extensions due to truncation
    # Check all possible partial truncations of each extension
    for ext in extensions:
        # Generate all possible partial extensions (from 1 char to full length-1)
        for length in range(1, len(ext)):
            partial_ext = ext[:length]  # e.g., '.', '.e', '.ex' for '.exe'
            if normalized.endswith(partial_ext):
                # Remove the partial extension
                return normalized[: -len(partial_ext)]

    # No extension found, return as-is
    return normalized


def is_process_match(target: str, found: str) -> bool:
    """Check if process names match with flexible rules."""
    target_norm = normalize_process_name(target)
    found_norm = normalize_process_name(found)

    # Exact match (preferred)
    if target_norm == found_norm:
        return True

    # Partial match (for truncated output)
    # Allow target to be a substring of found, or vice versa
    return target_norm in found_norm or found_norm in target_norm
