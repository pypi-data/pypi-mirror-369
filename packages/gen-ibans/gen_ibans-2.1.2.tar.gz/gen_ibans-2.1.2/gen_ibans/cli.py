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
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional
from click_option_group import optgroup
import math

from .iban_generator import IBANGenerator, IBANRecord, GeneratorConfig, LegalEntity
from .downloader import BundesbankDownloader
from .config_manager import (
    get_default_config_path,
    load_config_from_file,
    write_default_config_file,
    load_full_config,
)

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
    def _field_value(record: IBANRecord, field: str) -> str:
        field = field.strip().lower()
        if field == "iban":
            return record.iban
        elif field in ("bank_name", "bank-name", "bank"):
            return record.bank.name
        elif field == "bic":
            return record.bank.bic
        elif field in ("blz", "bank_code", "bankleitzahl", "code"):
            return record.bank.bankleitzahl
        elif field == "holders":
            return "; ".join(
                (
                    f"{h.name} (Legal Entity, WID: {h.wid})"
                    if isinstance(h, LegalEntity)
                    else f"{h.full_name} (Tax-ID: {h.tax_id}{', WID: ' + h.wid if getattr(h, 'wid', None) else ''})"
                )
                for h in record.account_holders
            )
        elif field == "beneficiaries":
            return (
                "; ".join(
                    (
                        f"{b.name} (Legal Entity, WID: {b.wid})"
                        if isinstance(b, LegalEntity)
                        else f"{b.full_name} (Tax-ID: {b.tax_id}{', WID: ' + b.wid if getattr(b, 'wid', None) else ''})"
                    )
                    for b in record.beneficiaries
                )
                or "None"
            )
        else:
            return ""

    @staticmethod
    def format_stdout(
        ibans: List[IBANRecord],
        include_bank_info: bool = True,
        include_personal_info: bool = True,
        fields: Optional[list[str]] = None,
    ) -> None:
        """Output IBANs to STDOUT."""
        for record in ibans:
            if fields:
                values = [OutputFormatter._field_value(record, f) for f in fields]
                print(" | ".join(v for v in values if v is not None))
                continue
            # Format account holders
            holders_str = []
            for holder in record.account_holders:
                if isinstance(holder, LegalEntity):
                    holders_str.append(
                        f"{holder.name} (Legal Entity, WID: {holder.wid})"
                    )
                else:
                    ids_str = f"Tax-ID: {holder.tax_id}"
                    if holder.wid:
                        ids_str += f", WID: {holder.wid}"
                    holders_str.append(f"{holder.full_name} ({ids_str})")
            holders_display = "; ".join(holders_str)

            # Format beneficiaries
            beneficiaries_str = []
            for beneficiary in record.beneficiaries:
                if isinstance(beneficiary, LegalEntity):
                    beneficiaries_str.append(
                        f"{beneficiary.name} (Legal Entity, WID: {beneficiary.wid})"
                    )
                else:
                    ids_str = f"Tax-ID: {beneficiary.tax_id}"
                    if beneficiary.wid:
                        ids_str += f", WID: {beneficiary.wid}"
                    beneficiaries_str.append(f"{beneficiary.full_name} ({ids_str})")
            beneficiaries_display = (
                "; ".join(beneficiaries_str) if beneficiaries_str else "None"
            )

            if include_personal_info and include_bank_info:
                print(
                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                )
            elif include_personal_info:
                print(
                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display}"
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
        fields: Optional[list[str]] = None,
    ) -> None:
        """Output IBANs to a text file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for record in ibans:
                    if fields:
                        values = [
                            OutputFormatter._field_value(record, fld) for fld in fields
                        ]
                        f.write(" | ".join(values) + "\n")
                        continue
                    # Format account holders
                    holders_str = []
                    for holder in record.account_holders:
                        if isinstance(holder, LegalEntity):
                            holders_str.append(
                                f"{holder.name} (Legal Entity, WID: {holder.wid})"
                            )
                        else:
                            ids_str = f"Tax-ID: {holder.tax_id}"
                            if holder.wid:
                                ids_str += f", WID: {holder.wid}"
                            holders_str.append(f"{holder.full_name} ({ids_str})")
                    holders_display = "; ".join(holders_str)

                    # Format beneficiaries
                    beneficiaries_str = []
                    for beneficiary in record.beneficiaries:
                        if isinstance(beneficiary, LegalEntity):
                            beneficiaries_str.append(
                                f"{beneficiary.name} (Legal Entity, WID: {beneficiary.wid})"
                            )
                        else:
                            ids_str = f"Tax-ID: {beneficiary.tax_id}"
                            if beneficiary.wid:
                                ids_str += f", WID: {beneficiary.wid}"
                            beneficiaries_str.append(
                                f"{beneficiary.full_name} ({ids_str})"
                            )
                    beneficiaries_display = (
                        "; ".join(beneficiaries_str) if beneficiaries_str else "None"
                    )

                    if include_personal_info and include_bank_info:
                        f.write(
                            f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}\n"
                        )
                    elif include_personal_info:
                        f.write(
                            f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display}\n"
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
        ibans: List[IBANRecord],
        output_path: str,
        clean: bool = False,
        fields: Optional[list[str]] = None,
    ) -> None:
        """Output IBANs to a CSV file."""
        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header
                if fields:
                    writer.writerow([fld for fld in fields])
                else:
                    writer.writerow(
                        [
                            "IBAN",
                            "Account Holders",
                            "Beneficial Owners",
                            "Bank Name",
                            "BIC",
                            "Bank Code",
                        ]
                    )

                # Write data
                for record in ibans:
                    if fields:
                        writer.writerow(
                            [
                                OutputFormatter._field_value(record, fld)
                                for fld in fields
                            ]
                        )
                        continue
                    # Format account holders
                    holders_str = []
                    for holder in record.account_holders:
                        if isinstance(holder, LegalEntity):
                            holders_str.append(
                                f"{holder.name} (Legal Entity, WID: {holder.wid})"
                            )
                        else:
                            ids_str = f"Tax-ID: {holder.tax_id}"
                            if holder.wid:
                                ids_str += f", WID: {holder.wid}"
                            holders_str.append(f"{holder.full_name} ({ids_str})")
                    holders_csv = "; ".join(holders_str)

                    # Format beneficiaries
                    beneficiaries_str = []
                    for beneficiary in record.beneficiaries:
                        if isinstance(beneficiary, LegalEntity):
                            beneficiaries_str.append(
                                f"{beneficiary.name} (Legal Entity, WID: {beneficiary.wid})"
                            )
                        else:
                            ids_str = f"Tax-ID: {beneficiary.tax_id}"
                            if beneficiary.wid:
                                ids_str += f", WID: {beneficiary.wid}"
                            beneficiaries_str.append(
                                f"{beneficiary.full_name} ({ids_str})"
                            )
                    beneficiaries_csv = (
                        "; ".join(beneficiaries_str) if beneficiaries_str else "None"
                    )

                    writer.writerow(
                        [
                            record.iban,
                            holders_csv,
                            beneficiaries_csv,
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
        ibans: List[IBANRecord],
        output_path: str,
        clean: bool = False,
        fields: Optional[list[str]] = None,
    ) -> None:
        """Output IBANs to an XML file."""
        try:
            root = ET.Element("accounts")

            for record in ibans:
                iban_elem = ET.SubElement(root, "account")
                if fields:
                    for fld in fields:
                        ET.SubElement(
                            iban_elem, fld
                        ).text = OutputFormatter._field_value(record, fld)
                    continue
                ET.SubElement(iban_elem, "iban").text = record.iban

                # Account holders
                holders_elem = ET.SubElement(iban_elem, "account_holders")
                for holder in record.account_holders:
                    holder_elem = ET.SubElement(holders_elem, "holder")
                    if isinstance(holder, LegalEntity):
                        ET.SubElement(holder_elem, "type").text = "legal_entity"
                        ET.SubElement(holder_elem, "name").text = holder.name
                        ET.SubElement(holder_elem, "wid").text = holder.wid
                        ET.SubElement(
                            holder_elem, "street_address"
                        ).text = holder.street_address
                        ET.SubElement(holder_elem, "city").text = holder.city
                        ET.SubElement(
                            holder_elem, "postal_code"
                        ).text = holder.postal_code
                    else:
                        ET.SubElement(holder_elem, "type").text = "natural_person"
                        ET.SubElement(
                            holder_elem, "first_name"
                        ).text = holder.first_name
                        ET.SubElement(holder_elem, "last_name").text = holder.last_name
                        ET.SubElement(holder_elem, "birth_date").text = str(
                            holder.birth_date
                        )
                        ET.SubElement(holder_elem, "tax_id").text = holder.tax_id
                        if holder.wid:
                            ET.SubElement(holder_elem, "wid").text = holder.wid
                        ET.SubElement(
                            holder_elem, "street_address"
                        ).text = holder.street_address
                        ET.SubElement(holder_elem, "city").text = holder.city
                        ET.SubElement(
                            holder_elem, "postal_code"
                        ).text = holder.postal_code

                # Beneficiaries
                beneficiaries_elem = ET.SubElement(iban_elem, "beneficiaries")
                for beneficiary in record.beneficiaries:
                    beneficiary_elem = ET.SubElement(beneficiaries_elem, "beneficiary")
                    if isinstance(beneficiary, LegalEntity):
                        ET.SubElement(beneficiary_elem, "type").text = "legal_entity"
                        ET.SubElement(beneficiary_elem, "name").text = beneficiary.name
                        ET.SubElement(beneficiary_elem, "wid").text = beneficiary.wid
                        ET.SubElement(
                            beneficiary_elem, "street_address"
                        ).text = beneficiary.street_address
                        ET.SubElement(beneficiary_elem, "city").text = beneficiary.city
                        ET.SubElement(
                            beneficiary_elem, "postal_code"
                        ).text = beneficiary.postal_code
                    else:
                        ET.SubElement(beneficiary_elem, "type").text = "natural_person"
                        ET.SubElement(
                            beneficiary_elem, "first_name"
                        ).text = beneficiary.first_name
                        ET.SubElement(
                            beneficiary_elem, "last_name"
                        ).text = beneficiary.last_name
                        ET.SubElement(beneficiary_elem, "birth_date").text = str(
                            beneficiary.birth_date
                        )
                        ET.SubElement(
                            beneficiary_elem, "tax_id"
                        ).text = beneficiary.tax_id
                        if beneficiary.wid:
                            ET.SubElement(
                                beneficiary_elem, "wid"
                            ).text = beneficiary.wid
                        ET.SubElement(
                            beneficiary_elem, "street_address"
                        ).text = beneficiary.street_address
                        ET.SubElement(beneficiary_elem, "city").text = beneficiary.city
                        ET.SubElement(
                            beneficiary_elem, "postal_code"
                        ).text = beneficiary.postal_code

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
        ibans: List[IBANRecord],
        output_path: str,
        clean: bool = False,
        fields: Optional[list[str]] = None,
    ) -> None:
        """Output IBANs to a JSON file."""
        try:
            data = []
            for record in ibans:
                if fields:
                    # Build a flat dict with requested fields
                    entry = {
                        fld: OutputFormatter._field_value(record, fld) for fld in fields
                    }
                    data.append(entry)
                    continue
                # Account holders
                holders_data = []
                for holder in record.account_holders:
                    if isinstance(holder, LegalEntity):
                        holders_data.append(
                            {
                                "type": "legal_entity",
                                "name": holder.name,
                                "wid": holder.wid,
                                "street_address": holder.street_address,
                                "city": holder.city,
                                "postal_code": holder.postal_code,
                            }
                        )
                    else:
                        holder_data = {
                            "type": "natural_person",
                            "first_name": holder.first_name,
                            "last_name": holder.last_name,
                            "birth_date": str(holder.birth_date),
                            "tax_id": holder.tax_id,
                            "street_address": holder.street_address,
                            "city": holder.city,
                            "postal_code": holder.postal_code,
                        }
                        if holder.wid:
                            holder_data["wid"] = holder.wid
                        holders_data.append(holder_data)

                # Beneficiaries
                beneficiaries_data = []
                for beneficiary in record.beneficiaries:
                    if isinstance(beneficiary, LegalEntity):
                        beneficiaries_data.append(
                            {
                                "type": "legal_entity",
                                "name": beneficiary.name,
                                "wid": beneficiary.wid,
                                "street_address": beneficiary.street_address,
                                "city": beneficiary.city,
                                "postal_code": beneficiary.postal_code,
                            }
                        )
                    else:
                        beneficiary_data = {
                            "type": "natural_person",
                            "first_name": beneficiary.first_name,
                            "last_name": beneficiary.last_name,
                            "birth_date": str(beneficiary.birth_date),
                            "tax_id": beneficiary.tax_id,
                            "street_address": beneficiary.street_address,
                            "city": beneficiary.city,
                            "postal_code": beneficiary.postal_code,
                        }
                        if beneficiary.wid:
                            beneficiary_data["wid"] = beneficiary.wid
                        beneficiaries_data.append(beneficiary_data)

                data.append(
                    {
                        "iban": record.iban,
                        "account_holders": holders_data,
                        "beneficiaries": beneficiaries_data,
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


class ColoredHelpCommand(click.Command):
    """Custom Click Command that adds colors to the help output.

    In addition to standard headers, this also highlights option group headers
    (from click-option-group) to make the help more scannable.
    """

    def get_help(self, ctx: click.Context) -> str:
        text = super().get_help(ctx)
        # Determine if we should colorize help (stdout context)
        no_color = False
        try:
            no_color = bool(ctx.params.get("no_color", False))
        except Exception:
            no_color = False
        enable_color = sys.stdout.isatty() and not no_color
        if not enable_color:
            return text

        def s(t: str, fg: Optional[str] = None, bold: bool = False) -> str:
            return click.style(t, fg=fg, bold=bold)

        # Color common section headers
        for header in ("Usage:", "Options:", "Arguments:", "Commands:"):
            if header in text:
                text = text.replace(header, s(header, fg="cyan", bold=True))

        # Color option flags and option group headers
        import re

        colored_lines = []
        group_header_pattern = re.compile(r"^(\s*)([^:\n][^:\n]*:)\s*$")
        for line in text.splitlines():
            # Highlight option group headers: lines ending with ':' (possibly indented)
            m_hdr = group_header_pattern.match(line)
            if m_hdr:
                indent, hdr = m_hdr.groups()
                # Avoid double-coloring for already-colored common headers
                if hdr not in {"Usage:", "Options:", "Arguments:", "Commands:"}:
                    line = f"{indent}{s(hdr, fg='bright_cyan', bold=True)}"
            else:
                # Match lines that look like options, e.g., "  -v, --version  Show version"
                m = re.match(r"(\s*)(-[^\s,][^\s]*?(?:,\s*--[^\s]+)?)(.*)", line)
                if m:
                    indent, flags, rest = m.groups()
                    line = (
                        f"{indent}{s(flags, fg='yellow', bold=True)}{s(rest, fg=None)}"
                    )
            colored_lines.append(line)
        return "\n".join(colored_lines)


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
    "--fields",
    type=str,
    help=(
        "Comma-separated list of fields to include in output (overrides iban_only/no_*). "
        "Supported fields: iban, bank_name, bic, blz, holders, beneficiaries"
    ),
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
    "--no-color",
    is_flag=True,
    help="Deaktiviere farbige Ausgabe (nur Schwarz/Weiß)",
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
@optgroup.group("Filter")
@optgroup.option(
    "--filter-bank-name",
    type=str,
    help="Regex to filter by bank name (case-insensitive)",
)
@optgroup.option(
    "--filter-bic",
    type=str,
    help="Regex to filter by BIC (case-insensitive)",
)
@optgroup.option(
    "--filter-blz",
    type=str,
    help="Regex to filter by BLZ/Bankleitzahl",
)
@optgroup.group("Entity Type Configuration")
@optgroup.option(
    "--legal-entity-probability",
    type=float,
    default=0.05,
    help="Probability of generating legal entity as sole account holder (default: 0.05 = 5%)",
)
@optgroup.group("Account Holders Distribution")
@optgroup.option(
    "--account-holder-single-prob",
    type=float,
    default=0.70,
    help="Probability of single account holder (default: 0.70 = 70%)",
)
@optgroup.option(
    "--account-holder-two-prob",
    type=float,
    default=0.15,
    help="Probability of two account holders (default: 0.15 = 15%)",
)
@optgroup.group("Beneficiaries Distribution")
@optgroup.option(
    "--beneficial-owner-zero-prob",
    type=float,
    default=0.70,
    help="Probability of zero beneficial owners (default: 0.70 = 70%)",
)
@optgroup.option(
    "--beneficial-owner-one-prob",
    type=float,
    default=0.20,
    help="Probability of one beneficial owner (default: 0.20 = 20%)",
)
@optgroup.group("Economic Activity Configuration")
@optgroup.option(
    "--economically-active-prob",
    type=float,
    default=0.20,
    help="Probability of natural persons being economically active (default: 0.20 = 20%)",
)
@optgroup.group("WID Unterscheidungsmerkmal (natürliche Personen)")
@optgroup.option(
    "--wid-feature-00000-prob",
    type=float,
    default=0.70,
    help="Wahrscheinlichkeit für kein Unterscheidungsmerkmal 00000 (Standard: 0.70 = 70%)",
)
@optgroup.option(
    "--wid-feature-00001-prob",
    type=float,
    default=0.10,
    help="Wahrscheinlichkeit für Unterscheidungsmerkmal 00001 (Standard: 0.10 = 10%)",
)
@optgroup.option(
    "--wid-feature-00002-00010-prob",
    type=float,
    default=0.099,
    help="Wahrscheinlichkeit für Unterscheidungsmerkmal im Bereich 00002–00010 (Standard: 0.099 = 9.9%)",
)
@optgroup.group("Person Reuse Distribution")
@optgroup.option(
    "--person-reuse-single-prob",
    type=float,
    default=0.90,
    help="Probability of single person use/no reuse (default: 0.90 = 90%)",
)
@optgroup.option(
    "--person-reuse-two-prob",
    type=float,
    default=0.05,
    help="Probability of person being used twice (default: 0.05 = 5%)",
)
@click.pass_context
def main(
    ctx: click.Context,
    data_file: Optional[Path],
    seed: int,
    count: int,
    output_format: str,
    output: Path,
    no_echo: bool,
    iban_only: bool,
    fields: Optional[str],
    no_personal_info: bool,
    no_bank_info: bool,
    clean: bool,
    no_color: bool,
    download_format: str,
    force_download: bool,
    cache_dir: Optional[Path],
    no_version_check: bool,
    filter_bank_name: Optional[str],
    filter_bic: Optional[str],
    filter_blz: Optional[str],
    legal_entity_probability: float,
    account_holder_single_prob: float,
    account_holder_two_prob: float,
    beneficial_owner_zero_prob: float,
    beneficial_owner_one_prob: float,
    economically_active_prob: float,
    wid_feature_00000_prob: float,
    wid_feature_00001_prob: float,
    wid_feature_00002_00010_prob: float,
    person_reuse_single_prob: float,
    person_reuse_two_prob: float,
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
      # Use automatically downloaded data (subcommand: gen)
      gen-ibans gen --count 5
      gen-ibans gen --count 10 --download-format xml

      # Use local data file
      gen-ibans gen data/blz-aktuell-csv-data.csv --count 5
      gen-ibans gen data/blz-aktuell-csv-data.csv --count 5 --format json
      gen-ibans gen data/blz-aktuell-csv-data.csv --count 5 --format txt --output ibans.txt
      gen-ibans gen data/blz-aktuell-csv-data.csv --count 5 --format csv --output ibans.csv --no-echo
      gen-ibans gen data/blz-aktuell-xml-data.xml --count 100 --format json --output ibans.json

      # Force re-download of data
      gen-ibans gen --count 5 --force-download
    """

    # Merge additional defaults from config file (CLI and downloader) if not provided on CLI
    merged = _merge_defaults(
        ctx,
        download_format=download_format,
        force_download=force_download,
        cache_dir=cache_dir,
        no_version_check=no_version_check,
        seed=seed,
        count=count,
        output_format=output_format,
        output=output,
        no_echo=no_echo,
        iban_only=iban_only,
        fields=fields,
        no_personal_info=no_personal_info,
        no_bank_info=no_bank_info,
        clean=clean,
        no_color=no_color,
        filter_bank_name=filter_bank_name,
        filter_bic=filter_bic,
        filter_blz=filter_blz,
    )
    download_format = merged["download_format"]
    force_download = merged["force_download"]
    cache_dir = merged["cache_dir"]
    no_version_check = merged["no_version_check"]
    seed = merged["seed"]
    count = merged["count"]
    output_format = merged["output_format"]
    output = merged["output"]
    no_echo = merged["no_echo"]
    iban_only = merged["iban_only"]
    no_personal_info = merged["no_personal_info"]
    no_bank_info = merged["no_bank_info"]
    clean = merged["clean"]
    no_color = merged["no_color"]
    # Apply filters from config if not provided on CLI
    filter_bank_name = merged.get("filter_bank_name", filter_bank_name)
    filter_bic = merged.get("filter_bic", filter_bic)
    filter_blz = merged.get("filter_blz", filter_blz)

    # Determine whether to enable colored output for CLI messages (stderr/info)
    enable_color = sys.stderr.isatty() and not no_color and not clean

    def style(text: str, fg: Optional[str] = None, bold: bool = False) -> str:
        return click.style(text, fg=fg, bold=bold) if enable_color else text

    # Validate arguments
    if count <= 0:
        raise click.BadParameter("Count must be a positive integer")

    try:
        # Determine data file to use (download if necessary)
        data_file_path = _determine_data_file_path(
            data_file=data_file,
            download_format=download_format,
            force_download=force_download,
            cache_dir=cache_dir,
            no_version_check=no_version_check,
            clean=clean,
            style=style,
        )

        # Build configuration from CLI + config file + defaults
        config = _build_generator_config(
            ctx,
            legal_entity_probability=legal_entity_probability,
            account_holder_single_prob=account_holder_single_prob,
            account_holder_two_prob=account_holder_two_prob,
            beneficial_owner_zero_prob=beneficial_owner_zero_prob,
            beneficial_owner_one_prob=beneficial_owner_one_prob,
            economically_active_prob=economically_active_prob,
            wid_feature_00000_prob=wid_feature_00000_prob,
            wid_feature_00001_prob=wid_feature_00001_prob,
            wid_feature_00002_00010_prob=wid_feature_00002_00010_prob,
            person_reuse_single_prob=person_reuse_single_prob,
            person_reuse_two_prob=person_reuse_two_prob,
        )

        # Hinweis zur Sichtbarkeit des Unterscheidungsmerkmals
        if not clean:
            try:
                le_prob = config.legal_entity_probability
                econ_prob = config.economically_active_probability
                if le_prob > 0.0 or econ_prob < 1.0:
                    hint_parts = []
                    if le_prob > 0.0:
                        hint_parts.append(
                            f"ein Teil ({le_prob * 100:.0f}%) der Datensätze sind juristische Personen ohne Unterscheidungsmerkmal"
                        )
                    if econ_prob < 1.0:
                        hint_parts.append(
                            f"ein Teil ({(1.0 - econ_prob) * 100:.0f}%) der natürlichen Personen ist nicht wirtschaftlich tätig (ohne WID)"
                        )
                    msg = (
                        "Hinweis: "
                        + "; ".join(hint_parts)
                        + ". Für 100% Unterscheidungsmerkmal ggf. --legal-entity-probability 0.0 und --economically-active-prob 1.0 setzen."
                    )
                    click.echo(style(msg, fg="yellow"), err=True)
            except Exception:
                pass

        # Initialize IBAN generator
        if not clean:
            click.echo(
                style(f"Loading bank data from: {data_file_path}", fg="cyan"), err=True
            )
        generator = IBANGenerator(data_file_path, seed, config)

        # Apply optional regex filters on bank list
        _apply_bank_filters(
            generator,
            filter_bank_name=filter_bank_name,
            filter_bic=filter_bic,
            filter_blz=filter_blz,
        )

        if not clean:
            click.echo(
                style(f"Loaded {generator.get_bank_count()} banks", fg="green"),
                err=True,
            )
            click.echo(style(f"Using seed: {generator.seed}", fg="magenta"), err=True)

        # Generate IBANs
        if not clean:
            click.echo(style(f"Generating {count} IBANs...", fg="cyan"), err=True)
        # Animated progress on stderr (TTY only) to avoid cluttering output
        show_progress = sys.stderr.isatty() and not clean
        # Dot-style spinner frames (braille dots)
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        last_msg_len = 0
        bar_width = 24
        start_time = time.time()

        def _fmt_eta(seconds: float) -> str:
            if seconds is None or math.isnan(seconds) or seconds == float("inf"):
                return "--:--"
            seconds = max(0, int(seconds))
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if h > 0:
                return f"{h:02d}:{m:02d}:{s:02d}"
            return f"{m:02d}:{s:02d}"

        # Determine what information to include (before generation loop)
        include_personal_info = not (no_personal_info or iban_only)
        include_bank_info = not (no_bank_info or iban_only)
        fields_list: Optional[list[str]] = merged.get("fields")
        output_to_stdout = not (no_echo and output)

        # Prepare file writers if output file is specified (streaming, no full in-memory list)
        file_handle = None
        csv_writer = None
        json_first = True
        try:
            if output:
                if not output_format:
                    raise click.BadParameter(
                        "--format is required when --output is specified"
                    )
                out_path = str(output)
                if output_format == "txt":
                    file_handle = open(out_path, "w", encoding="utf-8")
                elif output_format == "csv":
                    file_handle = open(out_path, "w", newline="", encoding="utf-8")
                    csv_writer = csv.writer(file_handle)
                    if fields_list:
                        csv_writer.writerow([fld for fld in fields_list])
                    else:
                        csv_writer.writerow(
                            [
                                "IBAN",
                                "Account Holders",
                                "Beneficial Owners",
                                "Bank Name",
                                "BIC",
                                "Bank Code",
                            ]
                        )
                elif output_format == "json":
                    file_handle = open(out_path, "w", encoding="utf-8")
                    file_handle.write("[")
                    json_first = True
                elif output_format == "xml":
                    file_handle = open(out_path, "w", encoding="utf-8")
                    file_handle.write(
                        '<?xml version="1.0" encoding="UTF-8"?>\n<accounts>\n'
                    )
                else:
                    raise click.BadParameter(f"Unsupported format: {output_format}")

            # Generation loop with streaming output
            for i in range(count):
                record = generator.generate_iban()

                # STDOUT streaming (if enabled)
                if output_to_stdout:
                    if output_format is None or output_format == "txt":
                        # Plain or TXT-like line output
                        if fields_list:
                            values = [
                                OutputFormatter._field_value(record, f)
                                for f in fields_list
                            ]
                            print(" | ".join(v for v in values if v is not None))
                        else:
                            holders_display = "; ".join(
                                _format_person_inline(h) for h in record.account_holders
                            )
                            beneficiaries_strs = [
                                _format_person_inline(b) for b in record.beneficiaries
                            ]
                            beneficiaries_display = (
                                "; ".join(beneficiaries_strs)
                                if beneficiaries_strs
                                else "None"
                            )
                            if include_personal_info and include_bank_info:
                                print(
                                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                                )
                            elif include_personal_info:
                                print(
                                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display}"
                                )
                            elif include_bank_info:
                                print(
                                    f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                                )
                            else:
                                print(record.iban)
                    elif output_format == "csv":
                        if fields_list:
                            if i == 0:
                                # print header
                                print(",".join(fields_list))
                            values = [
                                OutputFormatter._field_value(record, f)
                                for f in fields_list
                            ]
                            print(
                                ",".join(
                                    '"' + v.replace('"', '""') + '"' for v in values
                                )
                            )
                        else:
                            if i == 0:
                                print(
                                    "IBAN,Account Holders,Beneficial Owners,Bank Name,BIC,Bank Code"
                                )
                            holders_csv = "; ".join(
                                _format_person_inline(h) for h in record.account_holders
                            )
                            beneficiaries_strs = [
                                _format_person_inline(b) for b in record.beneficiaries
                            ]
                            beneficiaries_csv = (
                                "; ".join(beneficiaries_strs)
                                if beneficiaries_strs
                                else "None"
                            )
                            print(
                                f'"{record.iban}","{holders_csv}","{beneficiaries_csv}","{record.bank.name}","{record.bank.bic}","{record.bank.bankleitzahl}"'
                            )
                    elif output_format == "json":
                        # Stream ND-JSON to stdout as regular JSON array chunks
                        entry_obj = None
                        if fields_list:
                            entry_obj = {
                                f: OutputFormatter._field_value(record, f)
                                for f in fields_list
                            }
                        else:
                            entry_obj = {
                                "iban": record.iban,
                                "account_holders": [
                                    _person_to_dict(h) for h in record.account_holders
                                ],
                                "beneficiaries": [
                                    _person_to_dict(b) for b in record.beneficiaries
                                ],
                                "bank": {
                                    "name": record.bank.name,
                                    "bic": record.bank.bic,
                                    "code": record.bank.bankleitzahl,
                                },
                            }
                        # For stdout we can print the object per line (JSONL) to avoid buffering
                        print(json.dumps(entry_obj, ensure_ascii=False))
                    elif output_format == "xml":
                        # For stdout, print a minimal XML per record (not a full valid XML doc), to avoid buffering
                        # Users requesting XML to stdout should redirect to file; we keep memory low here
                        iban_elem = ET.Element("account")
                        if fields_list:
                            for f in fields_list:
                                ET.SubElement(
                                    iban_elem, f
                                ).text = OutputFormatter._field_value(record, f)
                        else:
                            ET.SubElement(iban_elem, "iban").text = record.iban
                            holders_elem = ET.SubElement(iban_elem, "account_holders")
                            for holder in record.account_holders:
                                _add_person_xml(holders_elem, "holder", holder)
                            beneficiaries_elem = ET.SubElement(
                                iban_elem, "beneficiaries"
                            )
                            for beneficiary in record.beneficiaries:
                                _add_person_xml(
                                    beneficiaries_elem, "beneficiary", beneficiary
                                )
                            bank_elem = ET.SubElement(iban_elem, "bank")
                            ET.SubElement(bank_elem, "name").text = record.bank.name
                            ET.SubElement(bank_elem, "bic").text = record.bank.bic
                            ET.SubElement(
                                bank_elem, "code"
                            ).text = record.bank.bankleitzahl
                        print(ET.tostring(iban_elem, encoding="unicode"))

                # FILE streaming (if enabled)
                if file_handle is not None:
                    if output_format == "txt":
                        if fields_list:
                            values = [
                                OutputFormatter._field_value(record, f)
                                for f in fields_list
                            ]
                            file_handle.write(" | ".join(values) + "\n")
                        else:
                            holders_display = "; ".join(
                                _format_person_inline(h) for h in record.account_holders
                            )
                            beneficiaries_strs = [
                                _format_person_inline(b) for b in record.beneficiaries
                            ]
                            beneficiaries_display = (
                                "; ".join(beneficiaries_strs)
                                if beneficiaries_strs
                                else "None"
                            )
                            if include_personal_info and include_bank_info:
                                file_handle.write(
                                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}\n"
                                )
                            elif include_personal_info:
                                file_handle.write(
                                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display}\n"
                                )
                            elif include_bank_info:
                                file_handle.write(
                                    f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}\n"
                                )
                            else:
                                file_handle.write(f"{record.iban}\n")
                    elif output_format == "csv":
                        if fields_list:
                            csv_writer.writerow(
                                [
                                    OutputFormatter._field_value(record, f)
                                    for f in fields_list
                                ]
                            )
                        else:
                            holders_csv = "; ".join(
                                _format_person_inline(h) for h in record.account_holders
                            )
                            beneficiaries_strs = [
                                _format_person_inline(b) for b in record.beneficiaries
                            ]
                            beneficiaries_csv = (
                                "; ".join(beneficiaries_strs)
                                if beneficiaries_strs
                                else "None"
                            )
                            csv_writer.writerow(
                                [
                                    record.iban,
                                    holders_csv,
                                    beneficiaries_csv,
                                    record.bank.name,
                                    record.bank.bic,
                                    record.bank.bankleitzahl,
                                ]
                            )
                    elif output_format == "json":
                        entry_obj = None
                        if fields_list:
                            entry_obj = {
                                f: OutputFormatter._field_value(record, f)
                                for f in fields_list
                            }
                        else:
                            entry_obj = {
                                "iban": record.iban,
                                "account_holders": [
                                    _person_to_dict(h) for h in record.account_holders
                                ],
                                "beneficiaries": [
                                    _person_to_dict(b) for b in record.beneficiaries
                                ],
                                "bank": {
                                    "name": record.bank.name,
                                    "bic": record.bank.bic,
                                    "code": record.bank.bankleitzahl,
                                },
                            }
                        if not json_first:
                            file_handle.write(",\n")
                        else:
                            file_handle.write("\n")
                            json_first = False
                        file_handle.write(
                            json.dumps(entry_obj, ensure_ascii=False, indent=None)
                        )
                    elif output_format == "xml":
                        # Build per-record XML element and write it out
                        iban_elem = ET.Element("account")
                        if fields_list:
                            for f in fields_list:
                                ET.SubElement(
                                    iban_elem, f
                                ).text = OutputFormatter._field_value(record, f)
                        else:
                            ET.SubElement(iban_elem, "iban").text = record.iban
                            holders_elem = ET.SubElement(iban_elem, "account_holders")
                            for holder in record.account_holders:
                                _add_person_xml(holders_elem, "holder", holder)
                            beneficiaries_elem = ET.SubElement(
                                iban_elem, "beneficiaries"
                            )
                            for beneficiary in record.beneficiaries:
                                _add_person_xml(
                                    beneficiaries_elem, "beneficiary", beneficiary
                                )
                            bank_elem = ET.SubElement(iban_elem, "bank")
                            ET.SubElement(bank_elem, "name").text = record.bank.name
                            ET.SubElement(bank_elem, "bic").text = record.bank.bic
                            ET.SubElement(
                                bank_elem, "code"
                            ).text = record.bank.bankleitzahl
                        # Pretty printing per record is expensive; write compact to save time/memory
                        file_handle.write(
                            "  " + ET.tostring(iban_elem, encoding="unicode") + "\n"
                        )

                # Update progress after processing (so write timing is included)
                if show_progress:
                    done = i + 1
                    MIN_ELAPSED_TIME = 1e-6
                    elapsed = max(MIN_ELAPSED_TIME, time.time() - start_time)
                    rate = done / elapsed
                    remaining = (count - done) / rate if rate > 0 else None
                    percent = int(done * 100 / count)
                    filled = int(bar_width * done / count)
                    bar = "#" * filled + "-" * (bar_width - filled)
                    frame = spinner_frames[i % len(spinner_frames)]
                    msg = f"{frame} [{bar}] {percent:3d}% {done}/{count} ETA: {_fmt_eta(remaining)}"
                    sys.stderr.write("\r" + msg)
                    if len(msg) < last_msg_len:
                        sys.stderr.write(" " * (last_msg_len - len(msg)))
                    sys.stderr.flush()
                    last_msg_len = len(msg)

            if show_progress:
                sys.stderr.write("\r" + " " * last_msg_len + "\r")
                sys.stderr.flush()

            # Finalize file outputs
            if file_handle is not None:
                if output_format == "json":
                    if not json_first:
                        file_handle.write("\n")
                    file_handle.write("]")
                elif output_format == "xml":
                    file_handle.write("</accounts>\n")
                file_handle.close()
                if not clean:
                    if output_format == "csv":
                        click.echo(
                            style(f"IBANs written to CSV: {out_path}", fg="green"),
                            err=True,
                        )
                    elif output_format == "xml":
                        click.echo(
                            style(f"IBANs written to XML: {out_path}", fg="green"),
                            err=True,
                        )
                    elif output_format == "json":
                        click.echo(
                            style(f"IBANs written to JSON: {out_path}", fg="green"),
                            err=True,
                        )
                    else:
                        click.echo(
                            style(f"IBANs written to: {out_path}", fg="green"), err=True
                        )

            if not clean:
                click.echo(
                    style(
                        f"Successfully generated {count} IBANs", fg="green", bold=True
                    ),
                    err=True,
                )
        finally:
            try:
                if file_handle and not file_handle.closed:
                    file_handle.close()
            except Exception:
                pass

    except Exception as e:
        raise click.ClickException(f"Error: {e}")


@click.command(help="Erstellt eine Default-Konfigurationsdatei an der Standard-Stelle")
@click.option(
    "--path",
    "path_opt",
    type=click.Path(path_type=Path),
    required=False,
    help="Optionaler Zielpfad für die Konfigurationsdatei",
)
@click.pass_context
def init_config(ctx: click.Context, path_opt: Optional[Path] = None) -> None:
    """CLI-Kommando: Default-Konfiguration schreiben und Speicherort ausgeben."""
    try:
        if path_opt:
            target = Path(path_opt)
        else:
            # Use global --config-dir if provided, otherwise OS default path
            cfg_dir = (
                (ctx.obj or {}).get("config_dir") if isinstance(ctx.obj, dict) else None
            )
            if cfg_dir:
                Path(cfg_dir).mkdir(parents=True, exist_ok=True)
                target = Path(cfg_dir) / "config.toml"
            else:
                target = get_default_config_path()
        created = write_default_config_file(target)
        click.echo(f"Default-Konfiguration wurde erstellt: {created}")
    except Exception as e:
        raise click.ClickException(
            f"Konfigurationsdatei konnte nicht erstellt werden: {e}"
        )


# Define a Click group to support subcommands like `gen` and `init`
@click.group(
    cls=click.Group,
    help="gen-ibans command suite with subcommands",
    invoke_without_command=True,
)
@click.option(
    "--config-dir",
    "global_config_dir",
    type=click.Path(path_type=Path, file_okay=False),
    required=False,
    help="Global: Ordner, in dem Konfigurationsdateien gesucht/geschrieben werden (wirkt auf Unterkommandos)",
)
@click.option("-v", "--version", is_flag=True, help="Show version and exit")
@click.option(
    "--show-config-path",
    is_flag=True,
    help="Zeige den Pfad zur Konfigurationsdatei und beende",
)
@click.pass_context
def cli(
    ctx: click.Context,
    global_config_dir: Optional[Path],
    version: bool,
    show_config_path: bool,
) -> None:
    """Command group entry point."""
    # Store global options for subcommands
    ctx.ensure_object(dict)
    if global_config_dir:
        ctx.obj["config_dir"] = Path(global_config_dir)
    # Handle version at top-level
    if version and ctx.invoked_subcommand is None:
        try:
            from importlib.metadata import version as _ver

            click.echo(_ver("gen-ibans"))
        except Exception:
            click.echo(__version__)
        ctx.exit(0)
    # Handle show-config-path at top-level
    if show_config_path and ctx.invoked_subcommand is None:
        click.echo(str(get_default_config_path()))
        ctx.exit(0)


# Register subcommands
cli.add_command(main, name="gen")
cli.add_command(init_config, name="init")


# Helper functions extracted from main to improve readability


def _merge_defaults(
    ctx: click.Context,
    *,
    download_format: str,
    force_download: bool,
    cache_dir: Optional[Path],
    no_version_check: bool,
    seed: Optional[int],
    count: int,
    output_format: Optional[str],
    output: Optional[Path],
    no_echo: bool,
    iban_only: bool,
    fields: Optional[str],
    no_personal_info: bool,
    no_bank_info: bool,
    clean: bool,
    no_color: bool,
    filter_bank_name: Optional[str],
    filter_bic: Optional[str],
    filter_blz: Optional[str],
):
    """Merge additional defaults from config file (CLI and downloader) if not provided on CLI.

    Returns a dict with possibly updated values.
    """
    try:
        provided_params = {
            param
            for param in ctx.params.keys()
            if ctx.get_parameter_source(param) != click.core.ParameterSource.DEFAULT
        }
        full_cfg = load_full_config()
        cli_cfg = full_cfg.get("cli", {}) or {}
        dl_cfg = full_cfg.get("downloader", {}) or {}
        # Downloader-related defaults
        if "download_format" not in provided_params and isinstance(
            dl_cfg.get("download_format"), str
        ):
            download_format = dl_cfg["download_format"]
        if "force_download" not in provided_params and isinstance(
            dl_cfg.get("force_download"), bool
        ):
            force_download = dl_cfg["force_download"]
        if "cache_dir" not in provided_params and dl_cfg.get("cache_dir"):
            try:
                cache_dir = (
                    Path(dl_cfg["cache_dir"]) if dl_cfg.get("cache_dir") else cache_dir
                )
            except Exception:
                pass
        if "no_version_check" not in provided_params and isinstance(
            dl_cfg.get("no_version_check"), bool
        ):
            no_version_check = dl_cfg["no_version_check"]
        # CLI-related defaults
        if "seed" not in provided_params and cli_cfg.get("seed") is not None:
            try:
                seed = int(cli_cfg["seed"])  # type: ignore
            except Exception:
                pass
        if "count" not in provided_params and isinstance(cli_cfg.get("count"), int):
            count = cli_cfg["count"]
        if "output_format" not in provided_params and cli_cfg.get("output_format"):
            output_format = cli_cfg.get("output_format")
        if "output" not in provided_params and cli_cfg.get("output"):
            try:
                output = Path(cli_cfg["output"])  # type: ignore
            except Exception:
                pass
        if "no_echo" not in provided_params and isinstance(
            cli_cfg.get("no_echo"), bool
        ):
            no_echo = cli_cfg["no_echo"]
        if "iban_only" not in provided_params and isinstance(
            cli_cfg.get("iban_only"), bool
        ):
            iban_only = cli_cfg["iban_only"]
        if "no_personal_info" not in provided_params and isinstance(
            cli_cfg.get("no_personal_info"), bool
        ):
            no_personal_info = cli_cfg["no_personal_info"]
        if "no_bank_info" not in provided_params and isinstance(
            cli_cfg.get("no_bank_info"), bool
        ):
            no_bank_info = cli_cfg["no_bank_info"]
        if "clean" not in provided_params and isinstance(cli_cfg.get("clean"), bool):
            clean = cli_cfg["clean"]
        if "no_color" not in provided_params and isinstance(
            cli_cfg.get("no_color"), bool
        ):
            no_color = cli_cfg["no_color"]
        # Fields selection: from config if not provided via CLI
        if "fields" not in provided_params and cli_cfg.get("fields") is not None:
            try:
                cfg_fields = cli_cfg.get("fields")
                if isinstance(cfg_fields, (list, tuple)):
                    fields = [str(f).strip() for f in cfg_fields if str(f).strip()]
                elif isinstance(cfg_fields, str):
                    fields = cfg_fields
            except Exception:
                pass
        # Filters: allow from config if not provided on CLI
        if "filter_bank_name" not in provided_params and cli_cfg.get(
            "filter_bank_name"
        ):
            try:
                # Empty strings are treated as unset
                fbn = str(cli_cfg.get("filter_bank_name"))
                filter_bank_name = fbn if fbn.strip() != "" else None  # type: ignore
            except Exception:
                pass
        if "filter_bic" not in provided_params and cli_cfg.get("filter_bic"):
            try:
                fbic = str(cli_cfg.get("filter_bic"))
                filter_bic = fbic if fbic.strip() != "" else None  # type: ignore
            except Exception:
                pass
        if "filter_blz" not in provided_params and cli_cfg.get("filter_blz"):
            try:
                fblz = str(cli_cfg.get("filter_blz"))
                filter_blz = fblz if fblz.strip() != "" else None  # type: ignore
            except Exception:
                pass
    except Exception:
        # Ignore config merge failures for non-generator settings
        pass

    # Normalize fields value to a list[str]
    normalized_fields: Optional[list[str]] = None
    try:
        if isinstance(fields, str):
            normalized_fields = [f.strip() for f in fields.split(",") if f.strip()]
        elif isinstance(fields, (list, tuple)):
            normalized_fields = [str(f).strip() for f in fields if str(f).strip()]
    except Exception:
        normalized_fields = None

    return {
        "download_format": download_format,
        "force_download": force_download,
        "cache_dir": cache_dir,
        "no_version_check": no_version_check,
        "seed": seed,
        "count": count,
        "output_format": output_format,
        "output": output,
        "no_echo": no_echo,
        "iban_only": iban_only,
        "no_personal_info": no_personal_info,
        "no_bank_info": no_bank_info,
        "clean": clean,
        "no_color": no_color,
        "filter_bank_name": filter_bank_name,
        "filter_bic": filter_bic,
        "filter_blz": filter_blz,
        "fields": normalized_fields,
    }


def _determine_data_file_path(
    *,
    data_file: Optional[Path],
    download_format: str,
    force_download: bool,
    cache_dir: Optional[Path],
    no_version_check: bool,
    clean: bool,
    style,
) -> str:
    """Determine the data file path, downloading if necessary."""
    if data_file is None:
        if not clean:
            click.echo(
                style(
                    f"No data file provided, downloading from Bundesbank ({download_format} format)...",
                    fg="yellow",
                ),
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
                click.echo(
                    style(f"Downloaded data cached at: {data_file_path}", fg="cyan"),
                    err=True,
                )
        except Exception as e:
            raise click.ClickException(f"Failed to download Bundesbank data: {e}")
    else:
        data_file_path = str(data_file)
    return data_file_path


def _apply_bank_filters(
    generator: IBANGenerator,
    *,
    filter_bank_name: Optional[str],
    filter_bic: Optional[str],
    filter_blz: Optional[str],
) -> None:
    """Apply optional regex filters to the generator's bank list."""
    try:
        import re as _re

        filtered_banks = generator.banks
        if filter_bank_name:
            pat_name = _re.compile(filter_bank_name, _re.IGNORECASE)
            filtered_banks = [
                b for b in filtered_banks if pat_name.search(b.name or "")
            ]
        if filter_bic:
            pat_bic = _re.compile(filter_bic, _re.IGNORECASE)
            filtered_banks = [b for b in filtered_banks if pat_bic.search(b.bic or "")]
        if filter_blz:
            pat_blz = _re.compile(filter_blz)
            filtered_banks = [
                b for b in filtered_banks if pat_blz.search(b.bankleitzahl or "")
            ]
        if filter_bank_name or filter_bic or filter_blz:
            generator.banks = filtered_banks
            if not generator.banks:
                raise click.ClickException("No banks match the provided filter(s).")
    except Exception as e:
        raise click.ClickException(f"Invalid filter regex provided: {e}")


def _get_provided_params(ctx: click.Context) -> set:
    return {
        param
        for param in ctx.params.keys()
        if ctx.get_parameter_source(param) != click.core.ParameterSource.DEFAULT
    }


def _convert_pairs_list(value):
    if isinstance(value, list):
        return [
            (int(p[0]), float(p[1]))
            for p in value
            if isinstance(p, (list, tuple)) and len(p) == 2
        ]
    return value


def _apply_config_file_values(config: GeneratorConfig, values: dict) -> None:
    for key, val in values.items():
        if key in {
            "account_holder_distribution",
            "beneficial_owner_distribution",
            "wid_feature_distribution",
            "person_reuse_distribution",
        }:
            val = _convert_pairs_list(val)
        try:
            setattr(config, key, val)
        except Exception:
            # Ignore unknown/mismatched keys
            pass


def _compose_account_holder_distribution(single: float, two: float):
    ah_remaining = 1.0 - single - two
    ah_ten_prob = ah_remaining * 0.933
    ah_hundred_prob = ah_remaining * 0.06
    ah_thousand_prob = ah_remaining * 0.007
    return [
        (1, single),
        (2, two),
        (10, ah_ten_prob),
        (100, ah_hundred_prob),
        (1000, ah_thousand_prob),
    ]


def _compose_beneficial_owner_distribution(zero: float, one: float):
    bo_remaining = 1.0 - zero - one
    bo_two_prob = bo_remaining * 0.5
    bo_ten_prob = bo_remaining * 0.4
    bo_fifty_prob = bo_remaining * 0.09
    bo_thousand_prob = bo_remaining * 0.01
    return [
        (0, zero),
        (1, one),
        (2, bo_two_prob),
        (10, bo_ten_prob),
        (50, bo_fifty_prob),
        (1000, bo_thousand_prob),
    ]


def _compose_wid_feature_distribution(
    p00000: float, p00001: float, p00002_00010: float
):
    # Clamp/normalize will be handled by caller; here we just compute remainder
    total = p00000 + p00001 + p00002_00010
    p_ge_00011 = max(0.0, 1.0 - total)
    return [
        (0, p00000),
        (1, p00001),
        (10, p00002_00010),
        (99999, p_ge_00011),
    ]


def _compose_person_reuse_distribution(single: float, two: float):
    pr_remaining = 1.0 - single - two
    pr_ten_prob = pr_remaining * 0.933
    pr_hundred_prob = pr_remaining * 0.06
    pr_thousand_prob = pr_remaining * 0.007
    return [
        (1, single),
        (2, two),
        (10, pr_ten_prob),
        (100, pr_hundred_prob),
        (1000, pr_thousand_prob),
    ]


def _build_generator_config(
    ctx: click.Context,
    *,
    legal_entity_probability: float,
    account_holder_single_prob: float,
    account_holder_two_prob: float,
    beneficial_owner_zero_prob: float,
    beneficial_owner_one_prob: float,
    economically_active_prob: float,
    wid_feature_00000_prob: float,
    wid_feature_00001_prob: float,
    wid_feature_00002_00010_prob: float,
    person_reuse_single_prob: float,
    person_reuse_two_prob: float,
) -> GeneratorConfig:
    """Build GeneratorConfig by merging config file values with CLI overrides."""
    # Base config from file and defaults
    config = GeneratorConfig()
    _apply_config_file_values(config, load_config_from_file())

    config_kwargs = {}
    provided_params = _get_provided_params(ctx)

    # Simple numeric overrides
    if "legal_entity_probability" in provided_params:
        config_kwargs["legal_entity_probability"] = legal_entity_probability
    if "economically_active_prob" in provided_params:
        config_kwargs["economically_active_probability"] = economically_active_prob

    # Distribution overrides (only when any related CLI value was provided)
    if any(
        p in provided_params
        for p in ("account_holder_single_prob", "account_holder_two_prob")
    ):
        config_kwargs["account_holder_distribution"] = (
            _compose_account_holder_distribution(
                account_holder_single_prob, account_holder_two_prob
            )
        )

    if any(
        p in provided_params
        for p in ("beneficial_owner_zero_prob", "beneficial_owner_one_prob")
    ):
        config_kwargs["beneficial_owner_distribution"] = (
            _compose_beneficial_owner_distribution(
                beneficial_owner_zero_prob, beneficial_owner_one_prob
            )
        )

    if any(
        p in provided_params
        for p in (
            "wid_feature_00000_prob",
            "wid_feature_00001_prob",
            "wid_feature_00002_00010_prob",
        )
    ):
        # Use current config values for unspecified params to avoid mixing with CLI defaults
        current_dist = getattr(
            config,
            "wid_feature_distribution",
            [(0, 0.70), (1, 0.10), (10, 0.099), (99999, 0.001)],
        )
        current_map = {k: v for k, v in current_dist}
        p0_provided = "wid_feature_00000_prob" in provided_params
        p1_provided = "wid_feature_00001_prob" in provided_params
        p2_provided = "wid_feature_00002_00010_prob" in provided_params
        p0 = wid_feature_00000_prob if p0_provided else current_map.get(0, 0.70)
        p1 = wid_feature_00001_prob if p1_provided else current_map.get(1, 0.10)
        p2 = wid_feature_00002_00010_prob if p2_provided else current_map.get(10, 0.099)
        # If the sum exceeds 1.0, normalize proportionally only among the provided values
        total = p0 + p1 + p2
        if total > 1.0:
            # Determine which were explicitly provided to preserve user intent
            provided_flags = [p0_provided, p1_provided, p2_provided]
            vals = [p0, p1, p2]
            if any(provided_flags):
                # Normalize only the provided subset, keep unspecified from current_map but cap final sum at 1.0
                norm_sum = sum(v for v, f in zip(vals, provided_flags) if f)
                if norm_sum > 0:
                    scaled = [
                        (v / norm_sum) if f else v for v, f in zip(vals, provided_flags)
                    ]
                    p0, p1, p2 = scaled
            else:
                # All came from defaults; normalize all
                p0, p1, p2 = (p0 / total, p1 / total, p2 / total)
        config_kwargs["wid_feature_distribution"] = _compose_wid_feature_distribution(
            p0, p1, p2
        )

    if any(
        p in provided_params
        for p in ("person_reuse_single_prob", "person_reuse_two_prob")
    ):
        config_kwargs["person_reuse_distribution"] = _compose_person_reuse_distribution(
            person_reuse_single_prob, person_reuse_two_prob
        )

    for key, val in config_kwargs.items():
        setattr(config, key, val)

    return config


def _format_person_inline(person) -> str:
    # Helper for txt/csv human-readable inline formatting
    if isinstance(person, LegalEntity):
        return f"{person.name} (Legal Entity, WID: {person.wid}), Address: {person.full_address}"
    else:
        ids_str = f"Tax-ID: {person.tax_id}"
        if getattr(person, "wid", None):
            ids_str += f", WID: {person.wid}"
        return f"{person.full_name} ({ids_str})"


def _person_to_dict(person) -> dict:
    # Helper for JSON formatting
    if isinstance(person, LegalEntity):
        return {
            "type": "legal_entity",
            "name": person.name,
            "wid": person.wid,
            "street_address": person.street_address,
            "city": person.city,
            "postal_code": person.postal_code,
        }
    else:
        d = {
            "type": "natural_person",
            "first_name": person.first_name,
            "last_name": person.last_name,
            "birth_date": str(person.birth_date),
            "tax_id": person.tax_id,
            "street_address": person.street_address,
            "city": person.city,
            "postal_code": person.postal_code,
        }
        if getattr(person, "wid", None):
            d["wid"] = person.wid
        return d


def _add_person_xml(parent: ET.Element, tag: str, person) -> None:
    # Helper for XML formatting
    elem = ET.SubElement(parent, tag)
    if isinstance(person, LegalEntity):
        ET.SubElement(elem, "type").text = "legal_entity"
        ET.SubElement(elem, "name").text = person.name
        ET.SubElement(elem, "wid").text = person.wid
        ET.SubElement(elem, "street_address").text = person.street_address
        ET.SubElement(elem, "city").text = person.city
        ET.SubElement(elem, "postal_code").text = person.postal_code
    else:
        ET.SubElement(elem, "type").text = "natural_person"
        ET.SubElement(elem, "first_name").text = person.first_name
        ET.SubElement(elem, "last_name").text = person.last_name
        ET.SubElement(elem, "birth_date").text = str(person.birth_date)
        ET.SubElement(elem, "tax_id").text = person.tax_id
        if getattr(person, "wid", None):
            ET.SubElement(elem, "wid").text = person.wid
        ET.SubElement(elem, "street_address").text = person.street_address
        ET.SubElement(elem, "city").text = person.city
        ET.SubElement(elem, "postal_code").text = person.postal_code


def _output_results_stdout(
    ibans: List[IBANRecord],
    *,
    output_format: Optional[str],
    include_bank_info: bool,
    include_personal_info: bool,
    fields: Optional[list[str]] = None,
) -> None:
    """Handle stdout output across supported formats (txt, csv, xml, json, or plain)."""
    formatter = OutputFormatter()
    if output_format is None:
        formatter.format_stdout(ibans, include_bank_info, include_personal_info, fields)
        return

    if output_format == "txt":
        for record in ibans:
            if fields:
                values = [OutputFormatter._field_value(record, f) for f in fields]
                print(" | ".join(values))
                continue
            holders_display = "; ".join(
                _format_person_inline(h) for h in record.account_holders
            )
            beneficiaries_strs = [
                _format_person_inline(b) for b in record.beneficiaries
            ]
            beneficiaries_display = (
                "; ".join(beneficiaries_strs) if beneficiaries_strs else "None"
            )

            if include_personal_info and include_bank_info:
                print(
                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                )
            elif include_personal_info:
                print(
                    f"{record.iban} | Holders: {holders_display} | Beneficiaries: {beneficiaries_display}"
                )
            elif include_bank_info:
                print(
                    f"{record.iban} | {record.bank.name} | {record.bank.bic} | {record.bank.bankleitzahl}"
                )
            else:
                print(record.iban)
    elif output_format == "csv":
        if fields:
            print(",".join(fields))
            for record in ibans:
                values = [OutputFormatter._field_value(record, f) for f in fields]
                # naive CSV quoting
                print(",".join('"' + v.replace('"', '""') + '"' for v in values))
        else:
            print("IBAN,Account Holders,Beneficial Owners,Bank Name,BIC,Bank Code")
            for record in ibans:
                holders_csv = "; ".join(
                    _format_person_inline(h) for h in record.account_holders
                )
                beneficiaries_strs = [
                    _format_person_inline(b) for b in record.beneficiaries
                ]
                beneficiaries_csv = (
                    "; ".join(beneficiaries_strs) if beneficiaries_strs else "None"
                )

                print(
                    f'"{record.iban}","{holders_csv}","{beneficiaries_csv}","{record.bank.name}","{record.bank.bic}","{record.bank.bankleitzahl}"'
                )
    elif output_format == "xml":
        import xml.dom.minidom

        root = ET.Element("accounts")
        for record in ibans:
            iban_elem = ET.SubElement(root, "account")
            if fields:
                for f in fields:
                    ET.SubElement(iban_elem, f).text = OutputFormatter._field_value(
                        record, f
                    )
                continue
            ET.SubElement(iban_elem, "iban").text = record.iban

        root = ET.Element("accounts")
        for record in ibans:
            iban_elem = ET.SubElement(root, "account")
            ET.SubElement(iban_elem, "iban").text = record.iban

            holders_elem = ET.SubElement(iban_elem, "account_holders")
            for holder in record.account_holders:
                _add_person_xml(holders_elem, "holder", holder)

            beneficiaries_elem = ET.SubElement(iban_elem, "beneficiaries")
            for beneficiary in record.beneficiaries:
                _add_person_xml(beneficiaries_elem, "beneficiary", beneficiary)

            bank_elem = ET.SubElement(iban_elem, "bank")
            ET.SubElement(bank_elem, "name").text = record.bank.name
            ET.SubElement(bank_elem, "bic").text = record.bank.bic
            ET.SubElement(bank_elem, "code").text = record.bank.bankleitzahl
        rough_string = ET.tostring(root, "utf-8")
        reparsed = xml.dom.minidom.parseString(rough_string)
        print(reparsed.toprettyxml(indent="  ").split("\n", 1)[1])
    elif output_format == "json":
        data = []
        for record in ibans:
            if fields:
                entry = {f: OutputFormatter._field_value(record, f) for f in fields}
                data.append(entry)
                continue
            holders_data = [_person_to_dict(h) for h in record.account_holders]
            beneficiaries_data = [_person_to_dict(b) for b in record.beneficiaries]
            data.append(
                {
                    "iban": record.iban,
                    "account_holders": holders_data,
                    "beneficiaries": beneficiaries_data,
                    "bank": {
                        "name": record.bank.name,
                        "bic": record.bank.bic,
                        "code": record.bank.bankleitzahl,
                    },
                }
            )
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
