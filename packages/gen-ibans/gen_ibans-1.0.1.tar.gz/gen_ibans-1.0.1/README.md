# German IBAN Generator

[![CI](https://github.com/swallat/gen-ibans/actions/workflows/ci.yml/badge.svg)](https://github.com/swallat/gen-ibans/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/gen-ibans.svg)](https://badge.fury.io/py/gen-ibans)
[![Python versions](https://img.shields.io/pypi/pyversions/gen-ibans.svg)](https://pypi.org/project/gen-ibans/)

A powerful tool for generating valid German IBANs using real Bundesbank data with deterministic PRNG and comprehensive format support.

## Inhaltsverzeichnis / Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Using uv (Recommended)](#using-uv-recommended)
  - [Using pip](#using-pip)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Output Formats](#output-formats)
  - [Output Control Options](#output-control-options)
  - [Advanced Options](#advanced-options)
  - [CLI Parameters Reference](#cli-parameters-reference)
  - [Python Module Usage](#python-module-usage)
  - [IBAN Validation](#iban-validation)
- [Data Sources](#data-sources)
  - [Automatic Download](#automatic-download)
  - [Supported Input Formats](#supported-input-formats)
- [Output Examples](#output-examples)
  - [Plain Text (Default)](#plain-text-default)
  - [JSON Format](#json-format)
  - [CSV Format](#csv-format)
  - [XML Format](#xml-format)
- [IBAN Format](#iban-format)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Development](#development)
  - [Prerequisites for Python Beginners](#prerequisites-for-python-beginners)
  - [Step 1: Install Python](#step-1-install-python)
  - [Step 2: Install mise (Python Version Manager)](#step-2-install-mise-python-version-manager)
  - [Step 3: Install uv (Fast Python Package Manager)](#step-3-install-uv-fast-python-package-manager)
  - [Step 4: Verify Your Setup](#step-4-verify-your-setup)
  - [Quick Setup with Bootstrap Scripts](#quick-setup-with-bootstrap-scripts)
  - [Releases](#releases)
  - [Local PyPI Publishing](#local-pypi-publishing)
  - [Project Structure](#project-structure)
  - [Requirements](#requirements)
  - [Testing](#testing)
  - [Building and Installation](#building-and-installation)

## Features

- ✅ **Valid IBAN Generation**: Creates mathematically correct German IBANs with proper check digits
- ✅ **Real Bank Data**: Uses authentic data from Deutsche Bundesbank (automatically downloaded or from local files)
- ✅ **Deterministic Generation**: PRNG with seeding for reproducible results
- ✅ **Automatic Data Download**: Fetches latest Bundesbank data automatically with smart caching
- ✅ **Version Checking**: Automatically detects and downloads newer data versions
- ✅ **Comprehensive CLI**: Full-featured command-line interface with extensive options
- ✅ **Personal Data**: Includes realistic German names and addresses using Faker

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd gen-ibans

# Install with uv
uv sync
```

### Using pip

```bash
pip install -e .
```

## Quick Start

```bash
# Generate 5 IBANs using automatically downloaded data
gen-ibans --count 5

# Generate IBANs with a specific seed for reproducibility
gen-ibans --count 10 --seed 12345

# Generate and save to JSON file
gen-ibans --count 100 --format json --output banks.json
```

## Usage

### Command Line Interface

The tool can be used with automatically downloaded data or local files:

#### Automatic Data Download (Recommended)
```bash
# Use latest data from Bundesbank (CSV format)
gen-ibans --count 5

# Force download of fresh data
gen-ibans --count 5 --force-download

# Use XML format from Bundesbank
gen-ibans --count 5 --download-format xml

# Disable version checking (use cached data)
gen-ibans --count 5 --no-version-check
```

#### Local Data Files
```bash
# Use local CSV file
gen-ibans data/blz-aktuell-csv-data.csv --count 5

# Use local TXT file
gen-ibans data/blz-aktuell-txt-data.txt --count 10

# Use local XML file
gen-ibans data/blz-aktuell-xml-data.xml --count 20
```

### Output Formats

```bash
# Plain text output (default)
gen-ibans --count 3

# JSON format to stdout
gen-ibans --count 3 --format json

# Save to CSV file
gen-ibans --count 100 --format csv --output results.csv

# Save to file without stdout echo
gen-ibans --count 50 --format json --output data.json --no-echo

# XML format
gen-ibans --count 10 --format xml --output banks.xml
```

### Output Control Options

```bash
# Only IBANs without any additional information
gen-ibans --count 5 --iban-only

# Exclude personal information
gen-ibans --count 5 --no-personal-info

# Exclude bank information
gen-ibans --count 5 --no-bank-info

# Clean mode: suppress all informational messages
gen-ibans --count 5 --clean
```

### Advanced Options

```bash
# Specify custom cache directory
gen-ibans --count 5 --cache-dir /path/to/cache

# Use specific seed for reproducible results
gen-ibans --count 10 --seed 42

# Multiple format example with all options
gen-ibans --count 20 --seed 12345 --format json --output detailed.json --download-format xml --clean
```

### CLI Parameters Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `data_file` | Path to local data file (optional if using auto-download) | *auto-download* |
| `--count` | Number of IBANs to generate | 1 |
| `--seed` | PRNG seed for deterministic generation | *random* |
| `--format` | Output format: txt, csv, xml, json | *plain text* |
| `--output` | Output file path | *stdout* |
| `--no-echo` | Suppress stdout when writing to file | *false* |
| `--iban-only` | Output only IBANs without additional data | *false* |
| `--no-personal-info` | Exclude personal information | *false* |
| `--no-bank-info` | Exclude bank information | *false* |
| `--clean` | Suppress informational messages | *false* |
| `--download-format` | Format for auto-download: csv, txt, xml | csv |
| `--force-download` | Force fresh download | *false* |
| `--cache-dir` | Custom cache directory | *system temp* |
| `--no-version-check` | Disable online version checking | *false* |

### Python Module Usage

```python
from gen_ibans import IBANGenerator

# Initialize with local file
generator = IBANGenerator('data/blz-aktuell-csv-data.csv', seed=12345)

# Generate single IBAN record
record = generator.generate_iban()
print(f"IBAN: {record.iban}")
print(f"Person: {record.person.full_name}")
print(f"Bank: {record.bank.name} ({record.bank.bic})")

# Generate multiple IBANs
records = generator.generate_ibans(10)
for record in records:
    print(f"{record.iban} | {record.person.full_name} | {record.bank.name}")

# Access bank information
print(f"Loaded {generator.get_bank_count()} banks")
print(f"Using seed: {generator.seed}")
```

### IBAN Validation

```python
from gen_ibans import validate_iban

# Validate IBAN
is_valid = validate_iban("DE89370400440532013000")
print(f"IBAN is valid: {is_valid}")
```

## Data Sources

### Automatic Download
The tool automatically downloads the latest bank data from Deutsche Bundesbank:
- **Source**: [Bundesbank Bank Code Download](https://www.bundesbank.de/de/aufgaben/unbarer-zahlungsverkehr/serviceangebot/bankleitzahlen/download-bankleitzahlen-602592)
- **Formats**: CSV, TXT, XML
- **Caching**: Smart caching with ETag-based version checking
- **Updates**: Automatic detection of newer data versions

### Supported Input Formats

1. **CSV Format**: Semicolon-separated with German encoding support
2. **TXT Format**: Fixed-width format as provided by Bundesbank
3. **XML Format**: Structured XML with namespace support

All formats support:
- UTF-8 and ISO-8859-1 encoding detection
- BOM (Byte Order Mark) handling
- German umlauts and special characters

## Output Examples

### Plain Text (Default)
```
DE48500700100000000001 | Max Mustermann | Musterstraße 1, 10115 Berlin | Deutsche Bank | DEUTDEBBXXX | 50070010
```

### JSON Format
```json
[
  {
    "iban": "DE48500700100000000001",
    "person": {
      "first_name": "Max",
      "last_name": "Mustermann",
      "street_address": "Musterstraße 1",
      "city": "Berlin",
      "postal_code": "10115"
    },
    "bank": {
      "name": "Deutsche Bank",
      "bic": "DEUTDEBBXXX",
      "code": "50070010"
    }
  }
]
```

### CSV Format
```csv
IBAN,First Name,Last Name,Street Address,City,Postal Code,Bank Name,BIC,Bank Code
DE48500700100000000001,Max,Mustermann,Musterstraße 1,Berlin,10115,Deutsche Bank,DEUTDEBBXXX,50070010
```

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ibans>
  <iban>
    <number>DE48500700100000000001</number>
    <person>
      <first_name>Max</first_name>
      <last_name>Mustermann</last_name>
      <street_address>Musterstraße 1</street_address>
      <city>Berlin</city>
      <postal_code>10115</postal_code>
    </person>
    <bank>
      <name>Deutsche Bank</name>
      <bic>DEUTDEBBXXX</bic>
      <code>50070010</code>
    </bank>
  </iban>
</ibans>
```

## Development

### Prerequisites for Python Beginners

If you're new to Python development, you'll need to install a few tools first. This section provides step-by-step instructions for setting up your development environment.

#### Step 1: Install Python

First, you need Python 3.8 or higher installed on your system.

##### On Windows:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **make sure to check "Add Python to PATH"**
3. Verify installation by opening Command Prompt and running:
   ```cmd
   python --version
   ```

##### On macOS:
1. Install using Homebrew (recommended):
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python
   ```
2. Or download from [python.org](https://www.python.org/downloads/)
3. Verify installation:
   ```bash
   python3 --version
   ```

##### On Linux (Ubuntu/Debian):
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip

# Verify installation
python3 --version
```

#### Step 2: Install mise (Python Version Manager)

mise is a tool that helps manage different versions of programming languages, including Python.

##### On Windows:
1. Install using PowerShell:
   ```powershell
   # Using winget (Windows Package Manager)
   winget install jdx.mise
   
   # Or using Scoop
   scoop install mise
   ```
2. Restart your terminal and verify:
   ```cmd
   mise --version
   ```

##### On macOS:
```bash
# Using Homebrew
brew install mise

# Or using curl
curl https://mise.run | sh

# Verify installation
mise --version
```

##### On Linux:
```bash
# Using curl
curl https://mise.run | sh

# Add to your shell profile (e.g., ~/.bashrc or ~/.zshrc)
echo 'eval "$(mise activate bash)"' >> ~/.bashrc

# Reload your shell or run:
source ~/.bashrc

# Verify installation
mise --version
```

#### Step 3: Install uv (Fast Python Package Manager)

uv is a modern, fast Python package manager that replaces pip in many workflows.

##### On Windows:
```powershell
# Using PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using winget
winget install --id=astral-sh.uv -e

# Verify installation
uv --version
```

##### On macOS:
```bash
# Using Homebrew
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

##### On Linux:
```bash
# Using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to your PATH (usually done automatically)
# If needed, add this to your ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

#### Step 4: Verify Your Setup

Once you have Python, mise, and uv installed, verify everything works:

```bash
# Check Python version (should be 3.8 or higher)
python --version

# Check mise
mise --version

# Check uv
uv --version
```

You're now ready to proceed with the development setup!

#### Quick Setup with Bootstrap Scripts

For a fully automated setup, you can use our platform-specific bootstrap scripts that will install all prerequisites and dependencies:

##### Windows (PowerShell)
```powershell
# Download and run the Windows bootstrap script
./bootstrap-windows.ps1
```

##### Linux (Debian/Ubuntu)
```bash
# Make script executable and run
chmod +x bootstrap-linux.sh
./bootstrap-linux.sh
```

##### macOS
```bash
# Make script executable and run
chmod +x bootstrap-macos.sh
./bootstrap-macos.sh
```

**What the bootstrap scripts do:**
- **Windows**: Installs Scoop, Python, mise, and uv automatically
- **Linux**: Installs Python, mise, and uv via apt and official installers
- **macOS**: Installs Homebrew, Python, mise, and uv automatically
- **All platforms**: Sets up shell integration and installs project dependencies

After running the bootstrap script, you can proceed directly to development!

### Releases

To create a new release of this project:

1. **Create and push a version tag**:
   ```bash
   # Create a new tag (replace x.y.z with your version number)
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Automatic process**: Once you push a tag starting with `v*`, GitHub Actions will automatically:
   - Run all tests across multiple Python versions and operating systems
   - Build the package using `uv build`
   - Create a GitHub release with release notes
   - Publish the package to PyPI (if `PYPI_TOKEN` secret is configured)

3. **Monitor the release**: Check the [Actions tab](https://github.com/swallat/gen-ibans/actions) to see the release progress.

### Local PyPI Publishing

If you want to publish to PyPI locally instead of using the automated GitHub Actions workflow, follow these steps:

#### Prerequisites

1. **PyPI Account**: You need a PyPI account and API token
2. **API Token**: Generate an API token from [PyPI Account Settings](https://pypi.org/manage/account/token/)

#### Step-by-Step Local Publishing

1. **Set up your PyPI API token**:
   ```bash
   # Option 1: Set as environment variable (recommended)
   $env:UV_PUBLISH_TOKEN="pypi-your-api-token-here"
   
   # Option 2: Or use uv's built-in credential storage
   uv publish --token "pypi-your-api-token-here" --dry-run
   ```

2. **Clean previous builds** (optional but recommended):
   ```bash
   Remove-Item -Recurse -Force dist\*
   ```

3. **Run tests** to ensure everything works:
   ```bash
   uv run pytest tests/ -v
   ```

4. **Build the package**:
   ```bash
   uv build
   ```
   This creates both wheel (`.whl`) and source distribution (`.tar.gz`) files in the `dist/` directory.

5. **Verify the build**:
   ```bash
   # Check what was built
   Get-ChildItem dist\
   
   # Optional: Install locally to test
   uv pip install dist\*.whl --force-reinstall
   ```

6. **Test publish** (dry run - highly recommended):
   ```bash
   uv publish --dry-run
   ```
   This simulates the upload without actually publishing.

7. **Publish to PyPI**:
   ```bash
   # Using environment variable
   uv publish
   
   # Or specify token directly
   uv publish --token "pypi-your-api-token-here"
   ```

#### Publishing to Test PyPI (Recommended for Testing)

Before publishing to the main PyPI, test with TestPyPI:

```bash
# Build the package
uv build

# Publish to Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/ --token "testpypi-your-api-token-here"

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ gen-ibans
```

#### Troubleshooting

- **Authentication errors**: Ensure your API token is correct and has upload permissions
- **Version conflicts**: PyPI doesn't allow re-uploading the same version. Increment your version tag
- **Build errors**: Check that all files are committed and your working directory is clean
- **Missing dependencies**: Run `uv sync --dev` to ensure all build dependencies are installed

#### Security Notes

- **Never commit API tokens** to version control
- **Use environment variables** or uv's credential storage for tokens
- **Limit token scope** to only the packages you need to upload
- **Revoke tokens** when no longer needed

### Project Structure
```
gen-ibans/
├── gen_ibans/                 # Main package
│   ├── __init__.py           # Package exports
│   ├── __main__.py           # CLI entry point
│   ├── cli.py                # Command-line interface
│   ├── iban_generator.py     # Core IBAN generation logic
│   └── downloader.py         # Bundesbank data downloader
├── tests/                    # Test suite
│   ├── test_cli.py          # CLI tests
│   ├── test_iban_generator.py # Generator tests
│   └── test_format_encoding.py # Format/encoding tests
├── data/                     # Sample data files
├── LICENSE                   # MIT license
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Requirements
- **Python**: 3.8 or higher
- **Dependencies**: 
  - `click >= 8.0.0` - CLI framework
  - `faker >= 20.0.0` - Fake data generation
- **Development Dependencies**:
  - `pytest >= 8.3.5` - Testing framework

### Testing

Run the comprehensive test suite:

```bash
# Run all tests with uv
uv run pytest tests/ -v

# Run specific test modules
uv run pytest tests/test_iban_generator.py -v
uv run pytest tests/test_cli.py -v
uv run pytest tests/test_format_encoding.py -v

# Run with unittest
python -m unittest discover tests -v
```

### Building and Installation

```bash
# Install development dependencies
uv sync --dev

# Install in development mode
uv pip install -e .

# Run tests
uv run pytest tests/
```

## IBAN Format

German IBANs follow this structure:
- **Length**: 22 characters
- **Format**: `DE` + 2 check digits + 8-digit bank code + 10-digit account number
- **Example**: `DE89370400440532013000`
- **Validation**: MOD-97 checksum algorithm

The tool generates IBANs with:
- Correct check digits using MOD-97 algorithm
- Valid German bank codes from real Bundesbank data
- Random but realistic account numbers
- Proper formatting and validation

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Sebastian Wallat

## Disclaimer

This tool generates IBANs with mathematically correct check digits based on real bank data from Deutsche Bundesbank. The generated IBANs are intended for **testing and development purposes only** and do not represent real bank accounts. 

**Do not use generated IBANs for actual financial transactions.**

The generated personal information (names, addresses) is fictional and created using the Faker library. Any resemblance to real persons is purely coincidental.