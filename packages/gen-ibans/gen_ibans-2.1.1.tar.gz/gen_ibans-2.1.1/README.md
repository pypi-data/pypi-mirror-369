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
  - [Bank Filter Options](#bank-filter-options)
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
- ✅ **Bank Filtering**: Regex-based filters for bank name, BIC, and BLZ (configurable via CLI or config file)
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
gen-ibans gen --count 5

# Generate IBANs with a specific seed for reproducibility
gen-ibans gen --count 10 --seed 12345

# Generate and save to JSON file
gen-ibans gen --count 100 --format json --output banks.json
```

## Usage

### Command Line Interface

The tool can be used with automatically downloaded data or local files:

#### Automatic Data Download (Recommended)
```bash
# Use latest data from Bundesbank (CSV format)
gen-ibans gen --count 5

# Force download of fresh data
gen-ibans gen --count 5 --force-download

# Use XML format from Bundesbank
gen-ibans gen --count 5 --download-format xml

# Disable version checking (use cached data)
gen-ibans gen --count 5 --no-version-check
```

#### Local Data Files
```bash
# Use local CSV file
gen-ibans gen data/blz-aktuell-csv-data.csv --count 5

# Use local TXT file
gen-ibans gen data/blz-aktuell-txt-data.txt --count 10

# Use local XML file
gen-ibans gen data/blz-aktuell-xml-data.xml --count 20
```

### Output Formats

```bash
# Plain text output (default)
gen-ibans gen --count 3

# JSON format to stdout
gen-ibans gen --count 3 --format json

# Save to CSV file
gen-ibans gen --count 100 --format csv --output results.csv

# Save to file without stdout echo
gen-ibans gen --count 50 --format json --output data.json --no-echo

# XML format
gen-ibans gen --count 10 --format xml --output banks.xml
```

### Output Control Options

```bash
# Only IBANs without any additional information
gen-ibans gen --count 5 --iban-only

# Exclude personal information
gen-ibans gen --count 5 --no-personal-info

# Exclude bank information
gen-ibans gen --count 5 --no-bank-info

# Clean mode: suppress all informational messages
gen-ibans gen --count 5 --clean
```

### Bank Filter Options

Use powerful regex filters to constrain which banks are used for IBAN generation.

```bash
# Filter by bank name (case-insensitive regex)
# Matches names containing "Sparkasse" or "Volksbank"
gen-ibans gen --count 5 --filter-bank-name "(Sparkasse|Volksbank)"

# Filter by BIC (case-insensitive regex)
# Example: all BICs starting with DEUTDEFF
gen-ibans gen --count 5 --filter-bic "DEUTDEFF.*"

# Filter by BLZ (Bankleitzahl) using regex (case-sensitive)
# Exact match example for 37040044
gen-ibans gen --count 5 --filter-blz "^37040044$"

# Combine multiple filters (banks must match ALL provided filters)
gen-ibans gen --count 5 --filter-bank-name "bundesbank" --filter-bic "markdeff.*"
```

Notes:
- filter-bank-name and filter-bic are matched with case-insensitive regex (re.IGNORECASE).
- filter-blz uses a case-sensitive regex (exact digits), so use anchors for exact matching.
- If no banks match the filters, the command fails with an error.
- Invalid regex patterns will raise an error with a helpful message.
- Filters can also be set in config.toml under the [cli] section.

### Advanced Options

```bash
# Specify custom cache directory
gen-ibans gen --count 5 --cache-dir /path/to/cache

# Use specific seed for reproducible results
gen-ibans gen --count 10 --seed 42

# Disable colored output
gen-ibans gen --count 5 --no-color

# Multiple format example with all options
gen-ibans gen --count 20 --seed 12345 --format json --output detailed.json --download-format xml --clean
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
| `--no-color` | Disable colored output (plain help/output) | *false* |
| `--download-format` | Format for auto-download: csv, txt, xml | csv |
| `--force-download` | Force fresh download | *false* |
| `--cache-dir` | Custom cache directory | *system temp* |
| `--no-version-check` | Disable online version checking | *false* |
| `--filter-bank-name` | Case-insensitive regex filter for bank name | — |
| `--filter-bic` | Case-insensitive regex filter for BIC | — |
| `--filter-blz` | Regex filter for BLZ (case-sensitive) | — |

### Konfiguration per Datei

Du kannst Standardwerte für die Generierung bequem über eine Konfigurationsdatei setzen. CLI-Parameter haben immer Vorrang gegenüber Werten aus der Datei.

- Standard-Speicherort (wird automatisch verwendet, wenn vorhanden):
  - Windows: %APPDATA%\gen-ibans\config.toml
  - Linux: ~/.config/gen-ibans/config.toml
  - macOS: ~/Library/Application Support/gen-ibans/config.toml

- Datei-Format: TOML. Die Datei ist ausführlich kommentiert und enthält zusätzlich auskommentierte Varianten.
  - [generator]: fachliche Generierungs-Parameter (Wahrscheinlichkeiten/Verteilungen)
  - [downloader]: Standardverhalten für automatischen Download (Format, Cache, Version-Check)
  - [cli]: Standardwerte für CLI-Optionen (count, seed, Ausgabeformat/-pfad, Flags)

- Beispielinhalt (Auszug):

```toml
# gen-ibans Konfigurationsdatei (TOML)
[generator]
# Wahrscheinlichkeit, dass der Kontoinhaber eine juristische Person ist (0..1).
legal_entity_probability = 0.05

# Wahrscheinlichkeit, dass natürliche Personen wirtschaftlich tätig sind (0..1).
economically_active_probability = 0.20

# Wahrscheinlichkeit, dass wirtschaftlich Berechtigte juristische Personen sind (derzeit 0).
beneficiary_legal_entity_probability = 0.0

# Verteilung der Anzahl der Kontoinhaber als Liste von [max_anzahl, wahrscheinlichkeit].
# Beispiel (Default): ein Inhaber 70%, zwei Inhaber 15%, bis 10: 14%, bis 100: 0.9%, bis 1000: 0.1%
account_holder_distribution = [[1, 0.70], [2, 0.15], [10, 0.14], [100, 0.009], [1000, 0.001]]
# Variante (kommentiert): höhere Mehrpersonenkonten
# account_holder_distribution = [[1, 0.60], [2, 0.25], [10, 0.13], [100, 0.019], [1000, 0.001]]

# Verteilung der Anzahl wirtschaftlich Berechtigter als Liste von [max_anzahl, wahrscheinlichkeit].
beneficial_owner_distribution = [[0, 0.70], [1, 0.20], [2, 0.05], [10, 0.04], [50, 0.009], [1000, 0.001]]
# Variante: häufiger 1 wirtschaftlich Berechtigter
# beneficial_owner_distribution = [[0, 0.50], [1, 0.35], [2, 0.10], [10, 0.04], [50, 0.009], [1000, 0.001]]

# WID Verteilung (nur natürliche Personen).
# 0 -> 00000 (Kein Unterscheidungsmerkmal), 1 -> 00001, 10 -> 00002-00010, 99999 -> >=00011 (00011-99999)
wid_feature_distribution = [[0, 0.70], [1, 0.10], [10, 0.099], [99999, 0.001]]
# Variante:
# wid_feature_distribution = [[0, 0.50], [1, 0.20], [10, 0.29], [99999, 0.01]]

# Wiederverwendung von Personen (wie oft dieselbe Person vorkommt) als [max_anzahl, wahrscheinlichkeit].
person_reuse_distribution = [[1, 0.8], [2, 0.1], [5, 0.05], [15, 0.03], [50, 0.019], [200, 0.001]]
# Variante: mehr Wiederverwendung im Long Tail
# person_reuse_distribution = [[1, 0.7], [2, 0.15], [5, 0.07], [15, 0.05], [50, 0.028], [200, 0.002]]

[downloader]
# Standardformat beim automatischen Download von der Bundesbank (csv|txt|xml).
download_format = "csv"
# Erzwinge Neu-Download auch wenn Cache vorhanden ist.
force_download = false
# Optionaler Cache-Ordner (Pfad als String).
# cache_dir = ".\\cache"
# Online-Versionsprüfung deaktivieren (nur Cache-Alter nutzen).
no_version_check = false

[cli]
# Standardanzahl zu generierender IBANs, wenn nicht per CLI angegeben.
count = 1
# Fester Seed für deterministische Ergebnisse (optional).
# seed = 12345
# Ausgabeformat (txt|csv|xml|json); leer bedeutet Plain-Text.
# output_format = "json"
# Ausgabedatei-Pfad; leer bedeutet stdout.
# output = ".\\ibans.json"
# Unterdrücke stdout, wenn in Datei geschrieben wird.
no_echo = false
# Nur IBANs ohne Bank- und Personendaten ausgeben.
iban_only = false
# Personenbezogene Daten ausblenden.
no_personal_info = false
# Bankinformationen ausblenden.
no_bank_info = false
# Zusätzliche Informationsmeldungen unterdrücken.
clean = false
# Farbige Ausgabe deaktivieren.
no_color = false
```

- Konfigurationsdatei erstellen (mit Standardwerten, Doku und Varianten):

```bash
# Zeige den verwendeten Konfigurationspfad an
gen-ibans --show-config-path

# Erstellt die Datei am Standard-Speicherort (siehe oben)
gen-ibans init

# Optional: an benutzerdefiniertem Pfad erstellen
gen-ibans init --path ".\\mein-config.toml"

# Optional: globales Zielverzeichnis über Gruppen-Option angeben (wirkt auf Unterkommandos)
# Beispiel: init schreibt dann nach ".\\mein-ordner\\config.toml"
gen-ibans --config-dir ".\\mein-ordner" init
```

Hinweise:
- Fehlt die Datei, werden Bibliotheks-Defaults verwendet.
- Werte aus der Datei werden automatisch geladen, können aber jederzeit per CLI-Option überschrieben werden (CLI > Datei > Defaults).

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
DE48500700100000000001 | Holders: Max Mustermann (Tax-ID: 12345678901, WID: DE0000001234-00001) | Beneficiaries: None | Deutsche Bank | DEUTDEBBXXX | 50070010
```

Notes:
- When multiple account holders exist, they are shown as a semicolon-separated list after "Holders:".
- Beneficiaries are shown similarly after "Beneficiaries:" or "None" if empty.

### JSON Format
```json
[
  {
    "iban": "DE48500700100000000001",
    "account_holders": [
      {
        "type": "natural_person",
        "first_name": "Max",
        "last_name": "Mustermann",
        "birth_date": "1990-01-01",
        "tax_id": "12345678901",
        "street_address": "Musterstraße 1",
        "city": "Berlin",
        "postal_code": "10115",
        "wid": "DE0000001234-00001"
      }
    ],
    "beneficiaries": [],
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
IBAN,Account Holders,Beneficial Owners,Bank Name,BIC,Bank Code
DE48500700100000000001,"Max Mustermann (Tax-ID: 12345678901, WID: DE0000001234-00001)","None","Deutsche Bank","DEUTDEBBXXX","50070010"
```

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<accounts>
  <account>
    <iban>DE48500700100000000001</iban>
    <account_holders>
      <holder>
        <type>natural_person</type>
        <first_name>Max</first_name>
        <last_name>Mustermann</last_name>
        <birth_date>1990-01-01</birth_date>
        <tax_id>12345678901</tax_id>
        <wid>DE0000001234-00001</wid>
        <street_address>Musterstraße 1</street_address>
        <city>Berlin</city>
        <postal_code>10115</postal_code>
      </holder>
    </account_holders>
    <beneficiaries />
    <bank>
      <name>Deutsche Bank</name>
      <bic>DEUTDEBBXXX</bic>
      <code>50070010</code>
    </bank>
  </account>
</accounts>
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
   # Create a new tag for the next release (don’t run until after merge into master/main)
   # Next planned release: v2.1.1
  # When ready:
  # git tag v2.1.1
  # git push origin v2.1.1
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

# Generate coverage and JUnit reports (configured in pytest.ini)
# Reports will be written to:
#  - JUnit XML:   reports\junit.xml
#  - Coverage XML: reports\coverage.xml
#  - Coverage HTML: reports\html\index.html
uv run pytest -q

# Run specific test modules
uv run pytest tests/test_iban_generator.py -v
uv run pytest tests/test_cli.py -v
uv run pytest tests/test_format_encoding.py -v

# Run with unittest
python -m unittest discover tests -v
```

Linting:

```bash
# Check with ruff
uv run ruff check

# Auto-fix where possible
uv run ruff check --fix
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