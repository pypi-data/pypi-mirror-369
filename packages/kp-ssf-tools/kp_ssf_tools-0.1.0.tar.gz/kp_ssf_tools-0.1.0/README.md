# SSF Tools - Forensic Analysis Toolkit

A forensic analysis toolkit for cybersecurity professionals performing PCI Secure Software Framework assessments and general forensic analysis.

## Features

- **Volatility Integration**: Automated memory analysis workflows using Volatility 3
- **Rich CLI Interface**: Beautiful, user-friendly command-line interface with colored output
- **Intelligent Process Matching**: Handles process name truncation and partial extension matching
- **File Collision Management**: Smart handling of existing files with user-controlled resolution
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

1. **Python 3.11+** - Required for the SSF Tools CLI
2. **Volatility 3** - Required for memory analysis

```bash
# Install Volatility 3 (recommended via pipx)
pipx install volatility3[full]

# Verify volatility installation
vol.exe --help  # Windows
vol --help       # Linux/macOS
```

### Install SSF Tools

```bash
# Clone the repository
git clone https://github.com/kirkpatrickprice/ssf-tools.git
cd ssf-tools

# Install with uv (recommended)
uv sync
uv run ssf_tools --help

# Or install with pip
pip install -e .
ssf_tools --help
```

## Usage

### Volatility Memory Analysis

The `volatility` sub-command performs comprehensive memory analysis on RAM images:

```bash
# Basic usage
ssf_tools volatility memory.dd windows interesting-processes.txt

# With custom options
ssf_tools volatility \
    --results-dir ./analysis_results \
    --pid-list-file custom-pids.txt \
    memory.dd windows interesting-processes.txt
```

#### Required Arguments:
- `IMAGE_FILE`: Path to the RAM image file (e.g., memory.dd)
- `PLATFORM`: Target platform (`windows`, `mac`, or `linux`)
- `INTERESTING_PROCESSES_FILE`: Text file with process names to analyze (one per line)

#### Optional Arguments:
- `--results-dir, -r`: Directory to save results (default: `<image_dir>/volatility/<image_name>`)
- `--pid-list-file, -p`: Filename for PID list output (default: `pid-list.txt`)

### Creating an Interesting Processes File

Create a text file with process names you want to analyze:

```text
notepad
chrome
firefox
svchost
explorer
powershell
lsass
```

The tool handles:
- Case-insensitive matching
- Partial matches (for truncated output)
- Extension flexibility (matches both `notepad` and `notepad.exe`)
- Multiple instances (automatically numbered: `svchost`, `svchost_2`, etc.)

## Workflow

The volatility command performs these steps:

1. **Extract Process List**: Runs `volatility pslist` to get all processes
2. **Match Interesting Processes**: Finds PIDs for your specified processes
3. **Extract File Handles**: Gets file handles for each interesting process
4. **Extract Memory Dumps**: Creates memory dumps for each process

## Output Files

Analysis results are saved to the results directory:

```
results/
├── pid-list.txt           # Raw volatility pslist output
├── interesting_pids.json  # Matched processes with PIDs
├── handles.txt            # File handles for all processes
└── *.dmp                  # Memory dump files (one per process)
```

## File Collision Handling

When files already exist, the tool prompts for resolution:

- **JSON files**: Overwrite, Append (merge), or Create new
- **Text files**: Overwrite, Append, or Create new  
- **Memory dumps**: Overwrite, Keep both (with timestamp), or Skip

## Examples

```bash
# Windows memory analysis
ssf_tools volatility memory.dd windows processes.txt

# Linux memory analysis with custom output
ssf_tools volatility --results-dir /tmp/analysis memory.lime linux interesting.txt

# macOS analysis
ssf_tools volatility osx_memory.dmg mac processes.txt
```

## Development

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.