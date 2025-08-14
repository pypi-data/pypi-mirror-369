"""
German IBAN Generator Module

This module provides functionality to generate valid German IBANs using
bank data from the Bundesbank CSV file and PRNG for deterministic generation.

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

import csv
import random
from typing import List, Optional
from dataclasses import dataclass
from faker import Faker


@dataclass
class PersonalInfo:
    """Represents personal information (name and address)."""

    first_name: str
    last_name: str
    street_address: str
    city: str
    postal_code: str

    @property
    def full_name(self) -> str:
        """Return the full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        """Return the full address."""
        return f"{self.street_address}, {self.postal_code} {self.city}"


@dataclass
class IBANRecord:
    """Complete record containing IBAN, bank info, and personal information."""

    iban: str
    bank: "BankInfo"
    person: PersonalInfo


class BankInfo:
    """Represents bank information from the CSV."""

    def __init__(self, bankleitzahl: str, bic: str, name: str):
        self.bankleitzahl = bankleitzahl
        self.bic = bic
        self.name = name

    def __repr__(self):
        return f"BankInfo(blz={self.bankleitzahl}, bic={self.bic}, name={self.name})"


class IBANGenerator:
    """Generates valid German IBANs using bank data and PRNG."""

    def __init__(self, csv_path: str, seed: Optional[int] = None):
        """
        Initialize the IBAN generator.

        Args:
            csv_path: Path to the Bundesbank CSV file
            seed: Optional PRNG seed for deterministic generation
        """
        self.banks: List[BankInfo] = []
        # If no seed provided, generate one for reproducibility tracking
        if seed is None:
            import time

            seed = int(time.time() * 1000000) % (2**32)
        self.seed = seed
        self.rng = random.Random(seed)
        self.faker = Faker("de_DE")
        self.faker.seed_instance(seed)
        self._load_banks(csv_path)

    def _load_banks(self, file_path: str) -> None:
        """Load bank data from CSV, TXT, or XML file."""
        from pathlib import Path

        file_extension = Path(file_path).suffix.lower()

        if file_extension == ".csv":
            self._load_banks_csv(file_path)
        elif file_extension == ".txt":
            self._load_banks_txt(file_path)
        elif file_extension == ".xml":
            self._load_banks_xml(file_path)
        else:
            # Try to detect format by trying CSV first, then TXT
            try:
                self._load_banks_csv(file_path)
            except Exception:
                try:
                    self._load_banks_txt(file_path)
                except Exception:
                    raise ValueError(
                        f"Unsupported file format or unable to parse file: {file_path}"
                    )

    def _load_banks_csv(self, csv_path: str) -> None:
        """Load bank data from CSV file."""
        # Try different encodings commonly used for German text files
        encodings = ["utf-8", "iso-8859-1", "windows-1252", "cp1252"]

        for encoding in encodings:
            try:
                with open(csv_path, "r", encoding=encoding) as file:
                    # Skip BOM if present
                    content = file.read()
                    if content.startswith("\ufeff"):
                        content = content[1:]

                    # Parse CSV
                    lines = content.splitlines()
                    reader = csv.reader(lines, delimiter=";")

                    # Skip header
                    next(reader)

                    for row in reader:
                        if len(row) >= 8:
                            bankleitzahl = row[0].strip('"')
                            bic = row[7].strip('"')
                            name = row[2].strip('"')

                            # Only include banks with valid BIC codes
                            if bic and len(bic) >= 8:
                                self.banks.append(BankInfo(bankleitzahl, bic, name))

                    # If we get here, the encoding worked
                    return

            except UnicodeDecodeError:
                # Try next encoding
                continue
            except Exception as e:
                raise ValueError(f"Error loading CSV file: {e}")

        # If we get here, none of the encodings worked
        raise ValueError(
            f"Could not decode CSV file with any of the supported encodings: {encodings}"
        )

    def _load_banks_txt(self, txt_path: str) -> None:
        """Load bank data from TXT file (fixed-width format)."""
        # Try different encodings commonly used for German text files
        encodings = ["utf-8", "iso-8859-1", "windows-1252", "cp1252"]

        for encoding in encodings:
            try:
                with open(txt_path, "r", encoding=encoding) as file:
                    content = file.read()
                    if content.startswith("\ufeff"):
                        content = content[1:]

                    lines = content.splitlines()

                    for line in lines:
                        if len(line) >= 139:  # Minimum length for a valid record
                            # Parse fixed-width format
                            # Positions based on analysis of the txt file:
                            # 0-8: Bank code (BLZ)
                            # 9-67: Bank name
                            # 68-102: Location
                            # 103-127: Short name
                            # 128-138: Some code
                            # 139+: BIC code

                            bankleitzahl = line[0:8].strip()
                            name = line[9:67].strip()
                            # BIC appears to be at position 139, but let's find it dynamically

                            # Extract BIC from the end part of the line
                            remaining = line[139:].strip() if len(line) > 139 else ""
                            bic = ""

                            # Look for BIC pattern (11 characters, letters and digits)
                            import re

                            bic_match = re.search(r"[A-Z0-9]{8,11}", remaining)
                            if bic_match:
                                bic = bic_match.group()

                            # Only include banks with valid BIC codes and bank codes
                            if (
                                bankleitzahl
                                and len(bankleitzahl) == 8
                                and bankleitzahl.isdigit()
                                and bic
                                and len(bic) >= 8
                            ):
                                self.banks.append(BankInfo(bankleitzahl, bic, name))

                    # If we get here, the encoding worked
                    return

            except UnicodeDecodeError:
                # Try next encoding
                continue
            except Exception as e:
                raise ValueError(f"Error loading TXT file: {e}")

        # If we get here, none of the encodings worked
        raise ValueError(
            f"Could not decode TXT file with any of the supported encodings: {encodings}"
        )

    def _load_banks_xml(self, xml_path: str) -> None:
        """Load bank data from XML file."""
        import xml.etree.ElementTree as ET

        # Try different encodings commonly used for German text files
        encodings = ["utf-8", "iso-8859-1", "windows-1252", "cp1252"]

        for encoding in encodings:
            try:
                # Parse the XML file with explicit encoding
                with open(xml_path, "r", encoding=encoding) as file:
                    content = file.read()
                    if content.startswith("\ufeff"):
                        content = content[1:]

                # Parse XML content
                root = ET.fromstring(content)

                # Define namespace for the XML
                namespace = {"ns": "urn:BBk:BLZ:xsd:BLZDat"}

                # Find all BLZEintrag elements (bank entries)
                entries = root.findall(".//ns:BLZEintrag", namespace)

                for entry in entries:
                    # Extract bank data
                    blz_elem = entry.find("ns:BLZ", namespace)
                    name_elem = entry.find("ns:Bezeichnung", namespace)
                    bic_elem = entry.find("ns:BIC", namespace)

                    if (
                        blz_elem is not None
                        and name_elem is not None
                        and bic_elem is not None
                    ):
                        bankleitzahl = blz_elem.text.strip() if blz_elem.text else ""
                        name = name_elem.text.strip() if name_elem.text else ""
                        bic = bic_elem.text.strip() if bic_elem.text else ""

                        # Only include banks with valid BIC codes and bank codes
                        if (
                            bankleitzahl
                            and len(bankleitzahl) == 8
                            and bankleitzahl.isdigit()
                            and bic
                            and len(bic) >= 8
                        ):
                            self.banks.append(BankInfo(bankleitzahl, bic, name))

                # If we get here, the encoding worked
                return

            except UnicodeDecodeError:
                # Try next encoding
                continue
            except ET.ParseError as e:
                raise ValueError(f"Error parsing XML file: {e}")
            except Exception as e:
                raise ValueError(f"Error loading XML file: {e}")

        # If we get here, none of the encodings worked
        raise ValueError(
            f"Could not decode XML file with any of the supported encodings: {encodings}"
        )

    def _calculate_iban_check_digits(
        self, bankleitzahl: str, account_number: str
    ) -> str:
        """
        Calculate IBAN check digits using the MOD-97 algorithm.

        Args:
            bankleitzahl: 8-digit German bank code
            account_number: 10-digit account number

        Returns:
            2-digit check digits as string
        """
        # German IBAN format: DE + check digits + bankleitzahl + account number
        # For check digit calculation: bankleitzahl + account number + "1314" + "00"
        # Where "1314" represents "DE" in numeric form (D=13, E=14)

        # Ensure account number is 10 digits, pad with leading zeros if needed
        account_number = account_number.zfill(10)

        # Create the string for MOD-97 calculation
        check_string = bankleitzahl + account_number + "1314" + "00"

        # Calculate MOD-97
        remainder = int(check_string) % 97
        check_digits = 98 - remainder

        return f"{check_digits:02d}"

    def _generate_account_number(self) -> str:
        """Generate a random 10-digit account number."""
        # Generate a random number between 1 and 9999999999 (10 digits max)
        # Avoid starting with 0 to ensure realistic account numbers
        account_num = self.rng.randint(1, 9999999999)
        return f"{account_num:010d}"

    def _generate_personal_info(self) -> PersonalInfo:
        """Generate personal information using Faker."""
        return PersonalInfo(
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            postal_code=self.faker.postcode(),
        )

    def generate_iban(self) -> IBANRecord:
        """
        Generate a single valid German IBAN with personal information.

        Returns:
            IBANRecord object containing IBAN, bank info, and personal information
        """
        if not self.banks:
            raise ValueError("No valid banks loaded from CSV")

        # Randomly select a bank
        bank = self.rng.choice(self.banks)

        # Generate random account number
        account_number = self._generate_account_number()

        # Calculate check digits
        check_digits = self._calculate_iban_check_digits(
            bank.bankleitzahl, account_number
        )

        # Construct IBAN
        iban = f"DE{check_digits}{bank.bankleitzahl}{account_number}"

        # Generate personal information
        person = self._generate_personal_info()

        return IBANRecord(iban=iban, bank=bank, person=person)

    def generate_ibans(self, count: int) -> List[IBANRecord]:
        """
        Generate multiple valid German IBANs with personal information.

        Args:
            count: Number of IBANs to generate

        Returns:
            List of IBANRecord objects containing IBAN, bank info, and personal information
        """
        if count <= 0:
            raise ValueError("Count must be positive")

        ibans = []
        for _ in range(count):
            ibans.append(self.generate_iban())

        return ibans

    def get_bank_count(self) -> int:
        """Return the number of loaded banks."""
        return len(self.banks)


def validate_iban(iban: str) -> bool:
    """
    Validate a German IBAN using the MOD-97 algorithm.

    Args:
        iban: The IBAN string to validate

    Returns:
        True if valid, False otherwise
    """
    if not iban or len(iban) != 22 or not iban.startswith("DE"):
        return False

    try:
        # Extract components
        check_digits = iban[2:4]
        bankleitzahl = iban[4:12]
        account_number = iban[12:22]

        # Verify all parts are numeric (except country code)
        if not (
            check_digits.isdigit()
            and bankleitzahl.isdigit()
            and account_number.isdigit()
        ):
            return False

        # MOD-97 validation: move first 4 characters to end and convert to numbers
        # DE -> 1314, so DEXX becomes XX1314
        rearranged = bankleitzahl + account_number + "1314" + check_digits

        # Calculate MOD-97
        remainder = int(rearranged) % 97

        return remainder == 1

    except (ValueError, IndexError):
        return False
