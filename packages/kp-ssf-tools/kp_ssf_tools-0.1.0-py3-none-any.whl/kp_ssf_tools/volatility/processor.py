"""Core volatility processing logic and workflow orchestration."""

import subprocess
from pathlib import Path

from kp_ssf_tools.core.rich_helpers import console, print_error, print_success
from kp_ssf_tools.core.utils import (
    get_volatility_command,
    validate_volatility_installation,
)
from kp_ssf_tools.volatility.file_manager import (
    append_to_handles_file,
    create_results_directory,
    rename_memory_dump_files,
    save_interesting_pids_json,
)
from kp_ssf_tools.volatility.models import ImagePlatforms, VolatilityInputModel
from kp_ssf_tools.volatility.parsers import find_interesting_pids, parse_pid_list


def run_volatility_command(command: list[str]) -> str:
    """Run a Volatility command and return the output."""
    try:
        console.print(f"[info]Running command:[/info] {' '.join(command)}")
        result = subprocess.run(  # noqa: S603
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as e:
        print_error(f"Volatility command failed: {e}")
        if e.stderr:
            console.print(f"[red]Error output:[/red] {e.stderr}")
        raise
    except (OSError, FileNotFoundError) as e:
        print_error(f"Failed to run command: {e}")
        raise
    else:
        return result.stdout


def extract_pid_list(input_model: VolatilityInputModel, results_dir: Path) -> Path:
    """Extract the list of all process IDs from the RAM capture image."""
    vol_command = get_volatility_command()

    # Determine PID list output file
    if input_model.pid_list_file:
        pid_list_file = results_dir / input_model.pid_list_file.name
    else:
        pid_list_file = results_dir / "pid-list.txt"

    # Build the volatility command
    command = [
        vol_command,
        "-f",
        str(input_model.image_file),
        f"{input_model.image_platform}.pslist",
    ]

    console.print("[info]Extracting process list...[/info]")
    output = run_volatility_command(command)

    # Save the results
    try:
        pid_list_file.write_text(output, encoding="utf-8")
        print_success(f"Saved PID list to: {pid_list_file}")
    except Exception as e:
        print_error(f"Failed to save PID list: {e}")
        raise

    return pid_list_file


def extract_file_handles(
    input_model: VolatilityInputModel,
    results_dir: Path,
    interesting_pids: dict[str, int],
) -> None:
    """Extract file handles for each interesting process."""
    vol_command = get_volatility_command()
    handles_file = results_dir / "handles.txt"

    console.print(
        f"[info]Extracting file handles for {len(interesting_pids)} processes...[/info]",
    )

    for process_name, pid in interesting_pids.items():
        console.print(
            f"[info]Extracting handles for {process_name} (PID {pid})...[/info]",
        )

        command = [
            vol_command,
            "-f",
            str(input_model.image_file),
            f"{input_model.image_platform}.handles",
            "--pid",
            str(pid),
        ]

        try:
            output = run_volatility_command(command)

            # Add header and append to handles file
            header = f"\n{'=' * 80}\n"
            header += f"File Handles for {process_name} (PID {pid})\n"
            header += f"{'=' * 80}\n"

            content = header + output
            append_to_handles_file(handles_file, content)

        except (subprocess.CalledProcessError, OSError, FileNotFoundError) as e:
            print_error(
                f"Failed to extract handles for {process_name} (PID {pid}): {e}",
            )
            continue

    print_success(f"File handles saved to: {handles_file}")


def extract_windows_sids(
    input_model: VolatilityInputModel,
    results_dir: Path,
    interesting_pids: dict[str, int],
) -> None:
    """Extract file handles for each interesting process."""
    vol_command = get_volatility_command()
    sids_file = results_dir / "sids.txt"

    console.print(
        f"[info]Extracting SIDs for {len(interesting_pids)} processes...[/info]",
    )

    for process_name, pid in interesting_pids.items():
        console.print(
            f"[info]Extracting SIDs for {process_name} (PID {pid})...[/info]",
        )

        command = [
            vol_command,
            "-f",
            str(input_model.image_file),
            f"{input_model.image_platform}.getsids",
            "--pid",
            str(pid),
        ]

        try:
            output = run_volatility_command(command)

            # Add header and append to SIDs file
            header = f"\n{'=' * 80}\n"
            header += f"SIDs for {process_name} (PID {pid})\n"
            header += f"{'=' * 80}\n"

            content = header + output
            append_to_handles_file(sids_file, content)

        except (subprocess.CalledProcessError, OSError, FileNotFoundError) as e:
            print_error(
                f"Failed to extract SIDs for {process_name} (PID {pid}): {e}",
            )
            continue

    print_success(f"SIDs saved to: {sids_file}")


def extract_windows_privileges(
    input_model: VolatilityInputModel,
    results_dir: Path,
    interesting_pids: dict[str, int],
) -> None:
    """Extract Windows privileges for each interesting process."""
    vol_command = get_volatility_command()
    privileges_file = results_dir / "privileges.txt"

    console.print(
        f"[info]Extracting privileges for {len(interesting_pids)} processes...[/info]",
    )

    for process_name, pid in interesting_pids.items():
        console.print(
            f"[info]Extracting privileges for {process_name} (PID {pid})...[/info]",
        )

        command = [
            vol_command,
            "-f",
            str(input_model.image_file),
            f"{input_model.image_platform}.privileges",
            "--pid",
            str(pid),
        ]

        try:
            output = run_volatility_command(command)

            # Add header and append to SIDs file
            header = f"\n{'=' * 80}\n"
            header += f"SIDs for {process_name} (PID {pid})\n"
            header += f"{'=' * 80}\n"

            content = header + output
            append_to_handles_file(privileges_file, content)

        except (subprocess.CalledProcessError, OSError, FileNotFoundError) as e:
            print_error(
                f"Failed to extract privileges for {process_name} (PID {pid}): {e}",
            )
            continue

    print_success(f"Privileges saved to: {privileges_file}")


def extract_memory_dumps(
    input_model: VolatilityInputModel,
    results_dir: Path,
    interesting_pids: dict[str, int],
) -> list[Path]:
    """Extract memory dumps for each interesting process."""
    vol_command = get_volatility_command()

    console.print(
        f"[info]Extracting memory dumps for {len(interesting_pids)} processes...[/info]",
    )

    # Track files created before and after each extraction to map process names to actual files
    extracted_files_mapping: dict[str, list[Path]] = {}

    for process_name, pid in interesting_pids.items():
        console.print(
            f"[info]Extracting memory dump for {process_name} (PID {pid})...[/info]",
        )

        # Get list of existing .dmp files before extraction
        existing_files = set(results_dir.glob("*.dmp"))

        command = [
            vol_command,
            "-f",
            str(input_model.image_file),
            "-o",
            str(results_dir),
            f"{input_model.image_platform}.memmap",
            "--pid",
            str(pid),
            "--dump",
        ]

        try:
            run_volatility_command(command)
            console.print(
                f"[success]Memory dump completed for {process_name}[/success]",
            )

            # Get list of .dmp files after extraction to identify new files
            new_files = set(results_dir.glob("*.dmp")) - existing_files

            # Filter for files that match this PID pattern (pid.{pid}*.dmp)
            pid_files = [f for f in new_files if f.name.startswith(f"pid.{pid}")]

            if pid_files:
                extracted_files_mapping[process_name] = pid_files
                console.print(
                    f"[info]Created {len(pid_files)} dump file(s) for {process_name}: "
                    f"{', '.join(f.name for f in pid_files)}[/info]",
                )
            else:
                console.print(
                    f"[warning]No dump files found for {process_name} (PID {pid})[/warning]",
                )

        except (subprocess.CalledProcessError, OSError, FileNotFoundError) as e:
            print_error(
                f"Failed to extract memory dump for {process_name} (PID {pid}): {e}",
            )
            continue

    # Rename the dump files with the improved mapping
    renamed_files = rename_memory_dump_files(
        results_dir,
        interesting_pids,
        extracted_files_mapping,
    )

    if renamed_files:
        print_success(f"Renamed {len(renamed_files)} memory dump files")

    return renamed_files


def run_volatility_workflow(input_model: VolatilityInputModel) -> None:
    """Run the complete Volatility workflow."""
    # Validate Volatility installation
    validate_volatility_installation()

    # Create results directory
    if input_model.results_dir:
        results_dir = input_model.results_dir
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = create_results_directory(
            input_model.image_file.parent,
            input_model.image_file,
        )

    console.print(
        f"[info]Starting Volatility workflow for:[/info] {input_model.image_file}",
    )
    console.print(f"[info]Platform:[/info] {input_model.image_platform}")
    console.print(f"[info]Results directory:[/info] {results_dir}")

    try:
        # Step 1: Extract PID list
        pid_list_file = extract_pid_list(input_model, results_dir)

        # Step 2: Parse PID list and find interesting processes
        processes, pid_content = parse_pid_list(
            pid_list_file,
            input_model.image_platform,
        )
        interesting_pids = find_interesting_pids(
            processes,
            input_model.interesting_processes_file,
            pid_content,
        )

        if not interesting_pids:
            console.print(
                "[yellow]No interesting processes found. Workflow completed.[/yellow]",
            )
            return

        # Step 3: Save interesting PIDs to JSON
        json_file = results_dir / "interesting_pids.json"
        save_interesting_pids_json(interesting_pids, json_file)

        # Step 4: Extract file handles
        extract_file_handles(input_model, results_dir, interesting_pids)

        # Step 5: Extract SIDs
        if input_model.image_platform == ImagePlatforms.WINDOWS:
            extract_windows_sids(input_model, results_dir, interesting_pids)

        # Step 6: Extract Windows Privileges
        if input_model.image_platform == ImagePlatforms.WINDOWS:
            extract_windows_privileges(input_model, results_dir, interesting_pids)

        # Step 6: Extract memory dumps
        extract_memory_dumps(input_model, results_dir, interesting_pids)

        console.print(
            "\n[success]Volatility workflow completed successfully![/success]",
        )
        console.print(f"[info]Results saved to:[/info] {results_dir}")

    except Exception as e:
        print_error(f"Workflow failed: {e}")
        raise
