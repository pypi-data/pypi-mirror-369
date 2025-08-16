"""File operations and collision handling for Volatility workflow."""

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

from kp_ssf_tools.core.rich_helpers import console, print_error, print_success


def resolve_directory_conflict(results_dir: Path) -> Path:
    """Handle directory name conflicts by prompting user for action."""
    if not results_dir.exists():
        return results_dir

    console.print(f"[warning]Directory already exists:[/warning] {results_dir}")
    console.print("\nWhat would you like to do?")
    console.print("1. [yellow]Provide a new name[/yellow]")
    console.print("2. [red]Delete all existing files[/red]")
    console.print("3. [blue]Quit[/blue]")

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                # Provide a new name
                new_name = input("Enter new directory name: ").strip()
                if not new_name:
                    console.print("[red]Invalid name. Please try again.[/red]")
                    continue

                new_results_dir = results_dir.parent / new_name
                if new_results_dir.exists():
                    console.print(
                        f"[red]Directory '{new_name}' also exists. Please choose another name.[/red]",
                    )
                    continue

                return new_results_dir

            if choice == "2":
                # Delete all existing files
                console.print(
                    f"[warning]Deleting all files in:[/warning] {results_dir}",
                )
                shutil.rmtree(results_dir)
                return results_dir

            if choice == "3":
                # Quit
                console.print("[blue]Operation cancelled by user[/blue]")
                raise SystemExit(0)

            console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")

        except KeyboardInterrupt:
            console.print("\n[blue]Operation cancelled by user[/blue]")
            raise SystemExit(0)  # noqa: B904


def create_results_directory(base_dir: Path, image_file: Path) -> Path:
    """Create the results directory structure."""
    # Create directory path: base_dir / "volatility" / image_file.stem
    results_dir = base_dir / "volatility" / image_file.stem

    # Handle conflicts if directory exists
    resolved_dir = resolve_directory_conflict(results_dir)

    # Create the directory structure
    resolved_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[success]Created results directory:[/success] {resolved_dir}")

    return resolved_dir


def save_interesting_pids_json(
    interesting_pids: dict[str, int],
    output_file: Path,
) -> None:
    """Save the interesting PIDs dictionary to a JSON file with pretty formatting."""
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(interesting_pids, f, indent=4, sort_keys=True)

        print_success(f"Saved interesting PIDs to: {output_file}")
        console.print(
            f"[info]Found {len(interesting_pids)} interesting processes[/info]",
        )

    except Exception as e:
        print_error(f"Failed to save interesting PIDs: {e}")
        raise


def rename_memory_dump_files(
    results_dir: Path,
    interesting_pids: dict[str, int],
    extracted_files_mapping: dict[str, list[Path]] | None = None,
) -> list[Path]:
    """
    Rename memory dump files from pid.{pid}*.dmp to {process_name}*.dmp.

    Args:
        results_dir: Directory containing the dump files
        interesting_pids: Mapping of process names to PIDs
        extracted_files_mapping: Optional mapping of process names to their actual dump files

    Returns:
        List of successfully renamed files

    """
    renamed_files: list[Path] = []

    for process_name, pid in interesting_pids.items():
        # Use the explicit mapping if provided, otherwise fall back to pattern matching
        if extracted_files_mapping and process_name in extracted_files_mapping:
            dump_files = extracted_files_mapping[process_name]
        else:
            # Fall back to searching for files matching the PID pattern
            dump_files = list(results_dir.glob(f"pid.{pid}*.dmp"))

        if not dump_files:
            console.print(
                f"[warning]No memory dump files found for {process_name} (PID {pid})[/warning]",
            )
            continue

        # Rename each dump file for this process
        for i, original_file in enumerate(dump_files):
            try:
                # Generate target filename
                if len(dump_files) == 1:
                    target_filename = f"{process_name}.dmp"
                else:
                    target_filename = f"{process_name}_{i + 1}.dmp"

                target_file = results_dir / target_filename

                # Handle conflicts if target file already exists
                if target_file.exists():
                    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
                    base_name = target_filename.replace(".dmp", "")
                    target_file = results_dir / f"{base_name}_{timestamp}.dmp"

                original_file.rename(target_file)
                renamed_files.append(target_file)
                console.print(
                    f"[success]Renamed:[/success] {original_file.name} → {target_file.name}",
                )

            except (OSError, FileNotFoundError) as e:
                print_error(f"Failed to rename {original_file}: {e}")

    return renamed_files


def append_to_handles_file(handles_file: Path, content: str) -> None:
    """Append content to the handles output file."""
    try:
        with handles_file.open("a", encoding="utf-8") as f:
            f.write(content)
            f.write("\n" + "=" * 80 + "\n")  # Add separator between entries

    except Exception as e:
        print_error(f"Failed to append to handles file: {e}")
        raise
