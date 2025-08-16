# Changelog

All notable changes to the German IBAN Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [2.1.2] - 2025-08-15

### Added
- CLI: New `--fields` option to select specific fields for output across stdout and file formats; also configurable via `[cli].fields` in config.toml.

### Changed
- PRNG: Explicitly documented and standardized on Python's Mersenne Twister (MT19937) via `random.Random` for deterministic generation. Added code comments and README notes. No behavioral change to outputs besides clearer guarantees.
- CLI: Progress indicator wording updated — replaced "Restzeit" with "ETA" in the generation progress message.
- README/Config: Expanded documentation for PRNG behavior and detailed explanation of person reuse (max_uses) distribution.

### Fixed
- Generator: Regularly prunes exhausted person entries from the reuse pool to prevent unbounded memory growth during long runs.

## [2.1.1] - 2025-08-14

### Changed
- Updated generated example configuration (config.toml) to current defaults of the new ID system:
  - WID feature distribution now includes 0 = 00000 (kein Unterscheidungsmerkmal) and adjusted probabilities
  - Comments updated to reflect new WID ranges (0, 1, 10, 99999)
- README updated:
  - Example configuration synchronized with generated file
  - Removed incorrect mention of legacy config.json backward compatibility

## [2.1.0] - 2025-08-14

### Added
- Regex-based bank filters in CLI:
  - `--filter-bank-name` (case-insensitive regex)
  - `--filter-bic` (case-insensitive regex)
  - `--filter-blz` (regex, case-sensitive for exact digit matches)
- Configurable filters via config file under `[cli]` (e.g., `filter_bank_name = "Bundesbank"`)
- `--no-color` option to disable colored output and help
- Improved colorized help with highlighted option group headers
- README updates: bank filter documentation, examples, and parameter table updates

### Changed
- Merged defaults from config file for CLI and downloader sections when CLI flags are not provided
- Enhanced error messages for invalid regex patterns and no-match scenarios

### Fixed
- Robust handling of filter application ordering and empty-result validation

## [2.0.0] - 2025-08-14

### Added
- New automated test reporting setup:
  - pytest.ini config to generate JUnit XML (reports\junit.xml) and coverage reports (XML and HTML in reports\)
  - Added pytest-cov to dev dependencies; documented in README
- Configuration via TOML using ConfZ with structured sections:
  - [generator]: probabilities and distributions for entity types, WID features, and person reuse
  - [downloader]: defaults for Bundesbank download (format, cache_dir, force_download, no_version_check)
  - [cli]: defaults for count, seed, output_format, output path and common flags (no_echo, iban_only, no_personal_info, no_bank_info, clean, no_color)
- New CLI options:
  - `--show-config-path` to print the effective default config path
  - `--config-dir` to influence where config files are searched/written (used with subcommands)
- New subcommand:
  - `gen-ibans init` to create a commented default `config.toml` (respects the top-level `--config-dir` when provided)
- Colorized CLI help with highlighted option group headers for improved readability

### Changed
- CLI structure: switched to subcommands. The former top-level command is now `gen-ibans gen`, and `gen-ibans-init-config` is now `gen-ibans init`.
- Standard config file switched from JSON to TOML; existing `config.json` files remain supported for backward compatibility
- Config file search path now prioritizes the current working directory and then the user config directory
- Help output: option group headers (click-option-group) are now highlighted consistently
- Output examples and documentation updated to reflect current JSON, CSV, and XML structures
- **XML Output Format**: Updated XML structure for better consistency
  - Root element changed from `<ibans>` to `<accounts>`
  - Individual entries changed from `<iban><number>` to `<account><iban>`
  - Maintains backward compatibility in terms of data content
- Added MIT license header to all newly added source and test files

### Fixed
- Robust handling of config loading with ConfZ fallback to manual parsing; graceful failure on malformed configs
- Improved stdout coloring control with `--no-color` and `--clean`

### Updated
- **Dependencies**: Added ConfZ and PlatformDirs; updated typing-extensions and related transitive dependencies

### Breaking Changes
- CLI now uses subcommands:
  - Generation is `gen-ibans gen ...` (was `gen-ibans ...`).
  - Config initialization is `gen-ibans init` (replaces separate `gen-ibans-init-config`).
- Global options moved to the top-level: use `gen-ibans --config-dir ... <subcommand>` and `gen-ibans --show-config-path`.
- The former `gen-ibans gen --write-default-config` option was removed. Use `gen-ibans init` (optionally with `--path` or top-level `--config-dir`).
- Default config format is now TOML (`config.toml`). Existing `config.json` files are still supported for backward compatibility, but new default files are written as TOML.

## [1.0.1] - 2025-08-13

Rerelease to push to PyPI.

## [1.0.0] - 2025-08-13

### Added
- **Core IBAN Generation**: Complete IBAN generator using real Bundesbank data
  - Valid German IBAN generation with proper MOD-97 check digits
  - Support for deterministic generation using PRNG with optional seeding
  - Automatic seed generation and display for reproducibility tracking
  
- **Multiple Input Format Support**:
  - CSV format support with semicolon-separated data
  - TXT format support for fixed-width Bundesbank data files
  - XML format support with proper namespace handling
  - Automatic format detection based on file extensions
  - Fallback format detection when extensions are ambiguous

- **Comprehensive Encoding Support**:
  - UTF-8 and ISO-8859-1 encoding detection and handling
  - BOM (Byte Order Mark) support for UTF-8 files
  - Automatic encoding fallback for robust file processing
  - Proper handling of German umlauts and special characters

- **Automatic Data Download**:
  - Automatic Bundesbank data download when no local file provided
  - Smart caching system with configurable cache directory
  - ETag-based version checking for automatic updates
  - Support for all three formats (CSV, TXT, XML) from Bundesbank
  - Configurable cache expiration and force download options

- **Rich CLI Interface**:
  - Comprehensive command-line interface using Click framework
  - Support for multiple output formats (plain text, TXT, CSV, XML, JSON)
  - Flexible output control (stdout, file output, or both)
  - Clean mode for automation (suppresses informational messages)
  - Granular control over included information (personal data, bank info)

- **Output Format Options**:
  - Plain text format with pipe-separated values (default)
  - Structured TXT files with configurable information
  - CSV format with proper headers and data organization
  - XML format with hierarchical structure and pretty printing
  - JSON format with nested objects for structured data

- **Personal Data Generation**:
  - Realistic German names and addresses using Faker library
  - Deterministic personal data generation tied to IBAN seed
  - Complete address information (street, city, postal code)
  - Consistent data generation for reproducible results

- **Advanced CLI Features**:
  - Version display with `-v`/`--version` flags
  - Seed display for reproducibility tracking
  - No-echo mode for file output without stdout display
  - Bank and personal information filtering options
  - Force download and cache management options
  - Version checking control with `--no-version-check`

- **Comprehensive Testing**:
  - 41+ test cases covering all functionality
  - Format and encoding test suite with multiple scenarios
  - CLI testing using Click's CliRunner
  - IBAN validation and generation testing
  - Cross-platform compatibility testing

- **Development Infrastructure**:
  - MIT license with proper copyright attribution
  - Comprehensive README with beginner-friendly setup instructions
  - Platform-specific bootstrap scripts (Windows, Linux, macOS)
  - Modern Python packaging with setuptools-scm
  - uv-based dependency management
  - GitHub Actions CI/CD workflows

- **Deployment and Distribution**:
  - Dynamic versioning based on git tags
  - Automated GitHub releases with artifact publishing
  - CI/CD pipeline for testing and deployment
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Python 3.8+ compatibility across all platforms

- **Documentation and Setup**:
  - Complete setup instructions for Python beginners
  - Bootstrap scripts for automated environment setup
  - Comprehensive CLI documentation with examples
  - Developer documentation with project structure
  - License headers in all source files

### Technical Details
- **Dependencies**: Click ≥8.0.0, Faker ≥20.0.0
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Platforms**: Windows, macOS, Linux (Debian-based)
- **Data Source**: Deutsche Bundesbank official bank code data
- **Validation**: MOD-97 algorithm for IBAN check digit calculation
- **Testing**: pytest-based test suite with comprehensive coverage

### Initial Release Features
This initial release provides a complete, production-ready IBAN generator with:
- Real bank data integration
- Multiple format support (input and output)
- Comprehensive CLI with extensive options
- Automatic data management and caching
- Cross-platform compatibility
- Professional development infrastructure
- Extensive documentation and setup automation

[Unreleased]: https://github.com/swallat/gen-ibans/compare/v2.1.2...HEAD
[2.1.2]: https://github.com/swallat/gen-ibans/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/swallat/gen-ibans/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/swallat/gen-ibans/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/swallat/gen-ibans/compare/v1.0.1...v2.0.0
[1.0.1]: https://github.com/swallat/gen-ibans/releases/tag/v1.0.1
[1.0.0]: https://github.com/swallat/gen-ibans/releases/tag/v1.0.0