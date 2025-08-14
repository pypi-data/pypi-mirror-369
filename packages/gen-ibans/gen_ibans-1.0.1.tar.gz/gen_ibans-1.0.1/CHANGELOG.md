# Changelog

All notable changes to the German IBAN Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/example/gen-ibans/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/example/gen-ibans/releases/tag/v0.1.0