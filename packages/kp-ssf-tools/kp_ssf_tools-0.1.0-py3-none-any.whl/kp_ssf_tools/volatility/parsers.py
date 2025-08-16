"""PID parsing and regex handling for Volatility output."""

import re
from collections import defaultdict
from pathlib import Path

from kp_ssf_tools.core.rich_helpers import console, print_warning
from kp_ssf_tools.core.utils import (
    handle_duplicate_process_names,
    is_process_match,
    read_text_file_lines,
    resolve_pid_conflicts,
)
from kp_ssf_tools.volatility.models import ImagePlatforms, ProcessEntry


def get_platform_regex(platform: ImagePlatforms) -> str:
    """Get the appropriate regex pattern for the given platform."""
    if platform == ImagePlatforms.WINDOWS:
        # Windows processes (case-insensitive, handles truncation)
        return r"(?P<pid>^\d+)\s+\d+\s+(?P<process_name>[A-Za-z0-9._-]+)\s+"
    # Linux/macOS processes (includes brackets, underscores, hyphens, slashes, colons)
    return r"(?P<pid>^\d+)\s+\d+\s+(?P<process_name>[\[\]A-Za-z0-9._/:-]+)\s+"


def parse_pid_list(
    pid_list_file: Path,
    platform: ImagePlatforms,
) -> tuple[list[ProcessEntry], str]:
    """
    Parse the Volatility PID list output file.

    Returns:
        Tuple of (list of ProcessEntry objects, raw file content)

    """
    console.print(f"[info]Parsing PID list from:[/info] {pid_list_file}")

    pid_regex = get_platform_regex(platform)
    pattern = re.compile(pid_regex, re.MULTILINE)

    processes: list[ProcessEntry] = []

    try:
        content = pid_list_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        content = pid_list_file.read_text(encoding="latin-1")

    for match in pattern.finditer(content):
        pid = int(match.group("pid"))
        process_name = match.group("process_name")
        processes.append(ProcessEntry(pid=pid, process_name=process_name))

    console.print(f"[success]Found {len(processes)} processes in PID list[/success]")
    return processes, content


def _match_processes_to_targets(
    processes: list[ProcessEntry],
    interesting_process_names: list[str],
) -> dict[str, list[int]]:
    """Match processes to target process names."""
    process_matches: dict[str, list[int]] = defaultdict(list)

    # Find matches for each interesting process
    for target_process in interesting_process_names:
        for process in processes:
            if is_process_match(target_process, process.process_name):
                process_matches[target_process].append(process.pid)

    return process_matches


def _report_found_processes(
    found_processes: list[str],
    resolved_matches: dict[str, list[int]],
) -> None:
    """Report successfully found processes."""
    if not found_processes:
        return

    console.print(
        f"[success]Found PIDs for {len(found_processes)} processes[/success]",
    )
    for process_name in found_processes:
        pids = resolved_matches[process_name]
        if len(pids) == 1:
            console.print(f"  • {process_name}: PID {pids[0]}")
        else:
            console.print(f"  • {process_name}: PIDs {pids} (multiple instances)")


def _handle_missing_processes(missing_processes: list[str]) -> None:
    """Handle missing processes and get user confirmation."""
    if not missing_processes:
        return

    print_warning(f"Could not find PIDs for {len(missing_processes)} processes:")
    for process_name in missing_processes:
        console.print(f"  • {process_name}")

    # Prompt user for confirmation
    console.print(
        "\n[yellow]Do you want to continue without these processes? (y/N):[/yellow] ",
        end="",
    )
    response = input().strip().lower()
    if response not in ("y", "yes"):
        console.print("[red]Operation cancelled by user[/red]")
        raise SystemExit(1)


def find_interesting_pids(
    processes: list[ProcessEntry],
    interesting_processes_file: Path,
    pid_list_content: str,
) -> dict[str, int]:
    """Find PIDs for interesting processes from the list."""
    console.print(
        f"[info]Reading interesting processes from:[/info] {interesting_processes_file}",
    )

    # Read the interesting processes list
    interesting_process_names = read_text_file_lines(interesting_processes_file)
    console.print(
        f"[info]Looking for {len(interesting_process_names)} interesting processes[/info]",
    )

    # Match processes to targets
    process_matches = _match_processes_to_targets(processes, interesting_process_names)

    # Resolve PID conflicts before handling duplicates
    resolved_matches, conflict_messages = resolve_pid_conflicts(
        process_matches,
        pid_list_content,
    )

    # Log conflict resolutions if any occurred
    if conflict_messages:
        console.print(f"\n[info]Resolved {len(conflict_messages)} PID conflicts[/info]")
        for msg in conflict_messages:
            console.print(f"  • {msg}")

    # Handle duplicates and create final mapping
    interesting_pids = handle_duplicate_process_names(resolved_matches)

    # Report findings
    found_processes = [
        name for name in interesting_process_names if name in resolved_matches
    ]
    missing_processes = [
        name for name in interesting_process_names if name not in resolved_matches
    ]

    _report_found_processes(found_processes, resolved_matches)
    _handle_missing_processes(missing_processes)

    return interesting_pids
