"""
CLI Interface for German IBAN Generator

Provides command-line interface with argument parsing and output formatting.

Copyright (c) 2025 Sebastian Wallat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import click
import csv
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional

from .iban_generator import IBANGenerator, IBANRecord
from .downloader import BundesbankDownloader

try:
    from importlib.metadata import version

    __version__ = version("gen-ibans")
except ImportError:
    # Fallback for older Python versions
    import pkg_resources

    __version__ = pkg_resources.get_distribution("gen-ibans").version


class OutputFormatter:
    """Handles different output formats for generated IBANs."""

    @staticmethod
    def format_stdout(
        ibans: List[IBANRecord],
        include_bank_info: bool = True,
        include_personal_info: bool = True,
    ) -> None:
        """Output IBANs to STDOUT."""
        for record in ibans:
            if include_personal_info and include_bank_info:
                print(
                    f"{record.iban} | {record.person.full_name} | {record.person.full_address} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                )
            elif include_personal_info:
                print(
                    f"{record.iban} | {record.person.full_name} | {record.person.full_address}"
                )
            elif include_bank_info:
                print(
                    f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                )
            else:
                print(record.iban)

    @staticmethod
    def format_txt(
        ibans: List[IBANRecord],
        output_path: str,
        include_bank_info: bool = True,
        include_personal_info: bool = True,
        clean: bool = False,
    ) -> None:
        """Output IBANs to a text file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for record in ibans:
                    if include_personal_info and include_bank_info:
                        f.write(
                            f"{record.iban} | {record.person.full_name} | {record.person.full_address} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}\n"
                        )
                    elif include_personal_info:
                        f.write(
                            f"{record.iban} | {record.person.full_name} | {record.person.full_address}\n"
                        )
                    elif include_bank_info:
                        f.write(
                            f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}\n"
                        )
                    else:
                        f.write(f"{record.iban}\n")
            if not clean:
                print(f"IBANs written to: {output_path}")
        except Exception as e:
            print(f"Error writing to file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def format_csv(
        ibans: List[IBANRecord], output_path: str, clean: bool = False
    ) -> None:
        """Output IBANs to a CSV file."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(
                    [
                        "IBAN",
                        "First Name",
                        "Last Name",
                        "Street Address",
                        "City",
                        "Postal Code",
                        "Bank Name",
                        "BIC",
                        "Bank Code",
                    ]
                )

                # Write data
                for record in ibans:
                    writer.writerow(
                        [
                            record.iban,
                            record.person.first_name,
                            record.person.last_name,
                            record.person.street_address,
                            record.person.city,
                            record.person.postal_code,
                            record.bank.name,
                            record.bank.bic,
                            record.bank.bankleitzahl,
                        ]
                    )

            if not clean:
                print(f"IBANs written to CSV: {output_path}")
        except Exception as e:
            print(f"Error writing to CSV file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def format_xml(
        ibans: List[IBANRecord], output_path: str, clean: bool = False
    ) -> None:
        """Output IBANs to an XML file."""
        try:
            root = ET.Element("ibans")

            for record in ibans:
                iban_elem = ET.SubElement(root, "iban")
                ET.SubElement(iban_elem, "number").text = record.iban

                # Personal info
                person_elem = ET.SubElement(iban_elem, "person")
                ET.SubElement(person_elem, "first_name").text = record.person.first_name
                ET.SubElement(person_elem, "last_name").text = record.person.last_name
                ET.SubElement(
                    person_elem, "street_address"
                ).text = record.person.street_address
                ET.SubElement(person_elem, "city").text = record.person.city
                ET.SubElement(
                    person_elem, "postal_code"
                ).text = record.person.postal_code

                # Bank info
                bank_elem = ET.SubElement(iban_elem, "bank")
                ET.SubElement(bank_elem, "name").text = record.bank.name
                ET.SubElement(bank_elem, "bic").text = record.bank.bic
                ET.SubElement(bank_elem, "code").text = record.bank.bankleitzahl

            # Write to file with proper formatting
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(output_path, encoding="utf-8", xml_declaration=True)

            if not clean:
                print(f"IBANs written to XML: {output_path}")
        except Exception as e:
            print(f"Error writing to XML file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def format_json(
        ibans: List[IBANRecord], output_path: str, clean: bool = False
    ) -> None:
        """Output IBANs to a JSON file."""
        try:
            data = []
            for record in ibans:
                data.append(
                    {
                        "iban": record.iban,
                        "person": {
                            "first_name": record.person.first_name,
                            "last_name": record.person.last_name,
                            "street_address": record.person.street_address,
                            "city": record.person.city,
                            "postal_code": record.person.postal_code,
                        },
                        "bank": {
                            "name": record.bank.name,
                            "bic": record.bank.bic,
                            "code": record.bank.bankleitzahl,
                        },
                    }
                )

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            if not clean:
                print(f"IBANs written to JSON: {output_path}")
        except Exception as e:
            print(f"Error writing to JSON file {output_path}: {e}", file=sys.stderr)
            sys.exit(1)


@click.command()
@click.argument(
    "data_file", type=click.Path(exists=True, path_type=Path), required=False
)
@click.option(
    "--seed", type=int, help="PRNG seed for deterministic generation (optional)"
)
@click.option(
    "--count", default=1, type=int, help="Number of IBANs to generate (default: 1)"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["txt", "csv", "xml", "json"]),
    help="Output format for file or stdout: txt, csv, xml, or json",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    help="Output file path (if not specified, output goes to stdout)",
)
@click.option(
    "--no-echo", is_flag=True, help="Suppress output to stdout when writing to a file"
)
@click.option(
    "--iban-only",
    is_flag=True,
    help="Output only IBANs without bank information or personal data",
)
@click.option(
    "--no-personal-info",
    is_flag=True,
    help="Exclude personal information (names and addresses) from output",
)
@click.option(
    "--no-bank-info", is_flag=True, help="Exclude bank information from output"
)
@click.option(
    "--clean",
    is_flag=True,
    help="Output only data without additional informational messages",
)
@click.option(
    "--download-format",
    type=click.Choice(["csv", "txt", "xml"]),
    default="csv",
    help="Format to download from Bundesbank when no data file is provided (default: csv)",
)
@click.option(
    "--force-download",
    is_flag=True,
    help="Force re-download even if cached data is available",
)
@click.option(
    "--cache-dir",
    type=click.Path(path_type=Path),
    help="Directory to cache downloaded data (default: system temp directory)",
)
@click.option(
    "--no-version-check",
    is_flag=True,
    help="Disable checking for newer versions online (rely only on cache age)",
)
@click.option("-v", "--version", is_flag=True, help="Show version and exit")
def main(
    data_file: Optional[Path],
    seed: int,
    count: int,
    output_format: str,
    output: Path,
    no_echo: bool,
    iban_only: bool,
    no_personal_info: bool,
    no_bank_info: bool,
    clean: bool,
    download_format: str,
    force_download: bool,
    cache_dir: Optional[Path],
    no_version_check: bool,
    version: bool,
) -> None:
    """Generate valid German IBANs using Bundesbank data.

    Data is always displayed on the command line by default in plain format.
    Use --format to specify alternative output formats (txt, csv, xml, json).
    Use --output to write to a file. Use --no-echo to suppress stdout when writing to files.

    If no DATA_FILE is provided, the latest data will be automatically downloaded
    from the Deutsche Bundesbank website and cached locally. The system automatically
    checks for newer versions online by comparing ETags, ensuring you always have
    current data. Use --no-version-check to disable this and rely only on cache age.

    Supports CSV, TXT, and XML input file formats.

    Examples:
      # Use automatically downloaded data
      gen-ibans --count 5
      gen-ibans --count 10 --download-format xml

      # Use local data file
      gen-ibans data/blz-aktuell-csv-data.csv --count 5
      gen-ibans data/blz-aktuell-csv-data.csv --count 5 --format json
      gen-ibans data/blz-aktuell-csv-data.csv --count 5 --format txt --output ibans.txt
      gen-ibans data/blz-aktuell-csv-data.csv --count 5 --format csv --output ibans.csv --no-echo
      gen-ibans data/blz-aktuell-xml-data.xml --count 100 --format json --output ibans.json

      # Force re-download of data
      gen-ibans --count 5 --force-download
    """
    # Handle version flag
    if version:
        click.echo(__version__)
        return

    # Validate arguments
    if count <= 0:
        raise click.BadParameter("Count must be a positive integer")

    try:
        # Determine data file to use
        if data_file is None:
            # Download data from Bundesbank
            if not clean:
                click.echo(
                    f"No data file provided, downloading from Bundesbank ({download_format} format)...",
                    err=True,
                )

            downloader = BundesbankDownloader(
                cache_dir=str(cache_dir) if cache_dir else None
            )
            try:
                data_file_path = downloader.get_data_file(
                    format_type=download_format,
                    force_download=force_download,
                    check_version=not no_version_check,
                )
                if not clean:
                    click.echo(f"Downloaded data cached at: {data_file_path}", err=True)
            except Exception as e:
                raise click.ClickException(f"Failed to download Bundesbank data: {e}")
        else:
            data_file_path = str(data_file)

        # Initialize IBAN generator
        if not clean:
            click.echo(f"Loading bank data from: {data_file_path}", err=True)
        generator = IBANGenerator(data_file_path, seed)
        if not clean:
            click.echo(f"Loaded {generator.get_bank_count()} banks", err=True)
            click.echo(f"Using seed: {generator.seed}", err=True)

        # Generate IBANs
        if not clean:
            click.echo(f"Generating {count} IBANs...", err=True)
        ibans = generator.generate_ibans(count)

        # Format and output results
        formatter = OutputFormatter()

        # Determine what information to include
        include_personal_info = not (no_personal_info or iban_only)
        include_bank_info = not (no_bank_info or iban_only)

        # Always output to stdout unless --no-echo is specified and --output is given
        output_to_stdout = not (no_echo and output)

        if output_to_stdout:
            if output_format:
                # Output in specified format to stdout
                if output_format == "txt":
                    # For txt format to stdout, use the same logic as format_txt but print to stdout
                    for record in ibans:
                        if include_personal_info and include_bank_info:
                            print(
                                f"{record.iban} | {record.person.full_name} | {record.person.full_address} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                            )
                        elif include_personal_info:
                            print(
                                f"{record.iban} | {record.person.full_name} | {record.person.full_address}"
                            )
                        elif include_bank_info:
                            print(
                                f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                            )
                        else:
                            print(record.iban)
                elif output_format == "csv":
                    # Output CSV format to stdout
                    print(
                        "IBAN,First Name,Last Name,Street Address,City,Postal Code,Bank Name,BIC,Bank Code"
                    )
                    for record in ibans:
                        print(
                            f"{record.iban},{record.person.first_name},{record.person.last_name},{record.person.street_address},{record.person.city},{record.person.postal_code},{record.bank.name},{record.bank.bic},{record.bank.bankleitzahl}"
                        )
                elif output_format == "xml":
                    # Output XML format to stdout
                    import xml.dom.minidom

                    root = ET.Element("ibans")
                    for record in ibans:
                        iban_elem = ET.SubElement(root, "iban")
                        ET.SubElement(iban_elem, "number").text = record.iban
                        person_elem = ET.SubElement(iban_elem, "person")
                        ET.SubElement(
                            person_elem, "first_name"
                        ).text = record.person.first_name
                        ET.SubElement(
                            person_elem, "last_name"
                        ).text = record.person.last_name
                        ET.SubElement(
                            person_elem, "street_address"
                        ).text = record.person.street_address
                        ET.SubElement(person_elem, "city").text = record.person.city
                        ET.SubElement(
                            person_elem, "postal_code"
                        ).text = record.person.postal_code
                        bank_elem = ET.SubElement(iban_elem, "bank")
                        ET.SubElement(bank_elem, "name").text = record.bank.name
                        ET.SubElement(bank_elem, "bic").text = record.bank.bic
                        ET.SubElement(bank_elem, "code").text = record.bank.bankleitzahl
                    # Pretty print XML to stdout
                    rough_string = ET.tostring(root, "utf-8")
                    reparsed = xml.dom.minidom.parseString(rough_string)
                    print(reparsed.toprettyxml(indent="  ").split("\n", 1)[1])
                elif output_format == "json":
                    # Output JSON format to stdout
                    data = []
                    for record in ibans:
                        data.append(
                            {
                                "iban": record.iban,
                                "person": {
                                    "first_name": record.person.first_name,
                                    "last_name": record.person.last_name,
                                    "street_address": record.person.street_address,
                                    "city": record.person.city,
                                    "postal_code": record.person.postal_code,
                                },
                                "bank": {
                                    "name": record.bank.name,
                                    "bic": record.bank.bic,
                                    "code": record.bank.bankleitzahl,
                                },
                            }
                        )
                    print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                # Default plain format (same as old stdout format)
                formatter.format_stdout(ibans, include_bank_info, include_personal_info)

        # Write to file if --output is specified
        if output:
            if not output_format:
                raise click.BadParameter(
                    "--format is required when --output is specified"
                )

            if output_format == "txt":
                formatter.format_txt(
                    ibans, str(output), include_bank_info, include_personal_info, clean
                )
            elif output_format == "csv":
                formatter.format_csv(ibans, str(output), clean)
            elif output_format == "xml":
                formatter.format_xml(ibans, str(output), clean)
            elif output_format == "json":
                formatter.format_json(ibans, str(output), clean)

        if not clean:
            click.echo(f"Successfully generated {len(ibans)} IBANs", err=True)

    except Exception as e:
        raise click.ClickException(f"Error: {e}")


if __name__ == "__main__":
    main()
