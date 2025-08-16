"""Data models for Volatility workflow."""

from enum import StrEnum
from pathlib import Path

from kp_ssf_tools.models.base import SSFToolsBaseModel


class ImagePlatforms(StrEnum):
    """Supported image platforms for Volatility analysis."""

    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"


class VolatilityInputModel(SSFToolsBaseModel):
    """User-supplied inputs for the Volatility workflow."""

    image_file: Path
    image_platform: ImagePlatforms
    pid_list_file: Path | None = None
    interesting_processes_file: Path
    results_dir: Path | None = None


class ProcessEntry(SSFToolsBaseModel):
    """Represents a process entry from the PID list."""

    pid: int
    process_name: str
    # Add more fields as needed from Volatility output


class InterestingPIDsModel(SSFToolsBaseModel):
    """Mapping of interesting process names to their PIDs."""

    interesting_pids: dict[str, int]


class HandlesFileResult(SSFToolsBaseModel):
    """Result of extracting file handles for a process."""

    pid: int
    process_name: str
    handles_output_file: Path


class MemoryDumpResult(SSFToolsBaseModel):
    """Result of extracting memory dump for a process."""

    pid: int
    process_name: str
    dump_file: Path
