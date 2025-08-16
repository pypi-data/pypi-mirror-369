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
from typing import List, Optional, Union
from dataclasses import dataclass, field
from datetime import date
from faker import Faker
from enum import Enum


class EntityType(Enum):
    """Enum for entity types."""

    NATURAL_PERSON = "natural_person"
    LEGAL_ENTITY = "legal_entity"


@dataclass
class PersonalInfo:
    """Represents personal information (name and address).

    Backward compatibility: Support older positional argument order where the
    7th argument was WID and the 8th was is_economically_active. If such usage
    is detected (birth_date provided as a WID-like string and wid provided as a
    boolean), the values will be reassigned accordingly.
    """

    first_name: str
    last_name: str
    street_address: str
    city: str
    postal_code: str
    tax_id: str  # Steuer-ID (always present for natural persons)
    birth_date: date  # Birth date for natural persons
    wid: Optional[str] = None  # WID (only for economically active persons)
    is_economically_active: bool = False  # Whether person is economically active

    def __post_init__(self):
        # Backward compatibility shim for older constructor order used in some tests
        # Detect if birth_date contains a WID-like string (e.g., starts with "DE" and digits)
        if (
            isinstance(self.birth_date, str)
            and self.birth_date.startswith("DE")
            and isinstance(self.wid, bool)
        ):
            # Treat provided birth_date as WID and provided wid (bool) as economic activity flag
            provided_wid = self.birth_date
            provided_active = bool(self.wid)
            # Assign reassigned values
            self.wid = provided_wid
            self.is_economically_active = provided_active
            # Set a default, but valid, birth_date (not used in current output formatting)
            # Use a fixed date for determinism
            self.birth_date = date(1990, 1, 1)

    @property
    def full_name(self) -> str:
        """Return the full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        """Return the full address."""
        return f"{self.street_address}, {self.postal_code} {self.city}"

    @property
    def ids(self) -> dict:
        """Return dictionary with available IDs."""
        result = {"tax_id": self.tax_id}
        if self.wid:
            result["wid"] = self.wid
        return result


@dataclass
class LegalEntity:
    """Represents a legal entity (company/organization)."""

    name: str
    street_address: str
    city: str
    postal_code: str
    wid: str

    @property
    def full_address(self) -> str:
        """Return the full address."""
        return f"{self.street_address}, {self.postal_code} {self.city}"


# Union type for account holders (either natural person or legal entity)
AccountHolder = Union[PersonalInfo, LegalEntity]


@dataclass
class IBANRecord:
    """Complete record containing IBAN, bank info, and account holder information."""

    iban: str
    bank: "BankInfo"
    account_holders: List[AccountHolder]
    beneficiaries: List[Union[PersonalInfo, LegalEntity]] = field(default_factory=list)

    @property
    def person(self) -> Optional[PersonalInfo]:
        """Backward compatibility: return first natural person account holder."""
        for holder in self.account_holders:
            if isinstance(holder, PersonalInfo):
                return holder
        return None

    @property
    def beneficial_owners(self) -> List[PersonalInfo]:
        """Backward compatibility: return only PersonalInfo beneficiaries."""
        return [b for b in self.beneficiaries if isinstance(b, PersonalInfo)]


@dataclass
class GeneratorConfig:
    """Configuration for IBAN generation with probability distributions."""

    # Account holder count distribution (probabilities sum to 1.0)
    account_holder_distribution: List[tuple] = field(
        default_factory=lambda: [
            (1, 0.70),  # 1 person: 70%
            (2, 0.15),  # 2 persons: 15%
            (10, 0.14),  # up to 10 persons: 14%
            (100, 0.009),  # up to 100 persons: 0.9%
            (1000, 0.001),  # up to 1000 persons: 0.1%
        ]
    )

    # Beneficial owner count distribution (probabilities sum to 1.0)
    beneficial_owner_distribution: List[tuple] = field(
        default_factory=lambda: [
            (0, 0.70),  # 0 beneficial owners: 70%
            (1, 0.20),  # 1 beneficial owner: 20%
            (2, 0.05),  # 2 beneficial owners: 5%
            (10, 0.04),  # up to 10 beneficial owners: 4%
            (50, 0.009),  # up to 50 beneficial owners: 0.9%
            (1000, 0.001),  # up to 1000 beneficial owners: 0.1%
        ]
    )

    # Probability of legal entity as sole account holder
    legal_entity_probability: float = 0.05  # 5% default

    # Probability of legal entity as beneficiary (currently 0%)
    beneficiary_legal_entity_probability: float = 0.0

    # Economic activity probability for natural persons (default: 80% non-active, 20% active)
    economically_active_probability: float = 0.20

    # WID distinguishing feature distribution
    # Note: 0 represents 'kein Unterscheidungsmerkmal' encoded as 00000 in the WID suffix
    wid_feature_distribution: List[tuple] = field(
        default_factory=lambda: [
            (0, 0.70),  # 00000 (kein Unterscheidungsmerkmal): 70%
            (1, 0.10),  # 00001: 10%
            (10, 0.099),  # 00002-00010: 9.9%
            (99999, 0.001),  # >=00011: 0.1% (00011-99999)
        ]
    )

    # Person reusability distribution (realistic exponential distribution)
    # Most people have 1-2 accounts, then exponentially decreasing probability
    person_reuse_distribution: List[tuple] = field(
        default_factory=lambda: [
            (1, 0.8),  # 1 account: 80%
            (2, 0.1),  # 2 accounts: 10%
            (5, 0.05),  # 3-5 accounts: 5%
            (15, 0.03),  # 6-15 accounts: 3%
            (50, 0.019),  # 16-50 accounts: 1.9%
            (200, 0.001),  # 51-200 accounts: 0.1%
        ]
    )

    def get_account_holder_count(self, rng: random.Random) -> int:
        """Get random account holder count based on distribution."""
        rand_val = rng.random()
        cumulative = 0.0
        for max_count, probability in self.account_holder_distribution:
            cumulative += probability
            if rand_val <= cumulative:
                if max_count == 1:
                    return 1
                return rng.randint(1, max_count)
        return 1  # fallback

    def get_beneficial_owner_count(self, rng: random.Random) -> int:
        """Get random beneficial owner count based on distribution."""
        rand_val = rng.random()
        cumulative = 0.0
        for max_count, probability in self.beneficial_owner_distribution:
            cumulative += probability
            if rand_val <= cumulative:
                if max_count == 0:
                    return 0
                return rng.randint(0, max_count)
        return 0  # fallback

    def should_be_legal_entity(self, rng: random.Random) -> bool:
        """Determine if account holder should be a legal entity."""
        return rng.random() < self.legal_entity_probability

    def should_be_economically_active(
        self, rng: random.Random, force_active: bool = False
    ) -> bool:
        """Determine if natural person should be economically active."""
        if force_active:
            return True
        return rng.random() < self.economically_active_probability

    def get_wid_distinguishing_feature(self, rng: random.Random) -> int:
        """Get random WID distinguishing feature based on distribution."""
        rand_val = rng.random()
        cumulative = 0.0
        for max_val, probability in self.wid_feature_distribution:
            cumulative += probability
            if rand_val <= cumulative:
                if max_val == 0:
                    return 0  # Kein Unterscheidungsmerkmal -> 00000
                elif max_val == 1:
                    return 1  # Always 00001
                elif max_val == 10:
                    return rng.randint(2, 10)  # 00002-00010
                elif max_val == 100:
                    return rng.randint(11, 100)  # 00011-00100
                else:
                    return rng.randint(11, 99999)  # >=00011 (00011-99999)
        return 0  # fallback to 'kein Unterscheidungsmerkmal'

    def get_person_reuse_count(self, rng: random.Random) -> int:
        """Sample the planned max_uses for a base person from a distribution.

        Definition of max_uses:
        - We interpret person_reuse_distribution as a list of buckets of the
          form (max_count, probability). Probabilities should sum to ~1.0.
        - First, we pick a bucket according to its probability.
        - Then we uniformly sample an integer in the inclusive range
          [1, max_count]. The sampled value is the person's planned total
          number of uses (max_uses) across the dataset.
        - A value of 1 means the person will be used exactly once (no reuse).

        Example with default distribution:
        [(1, 0.8), (2, 0.1), (5, 0.05), (15, 0.03), (50, 0.019), (200, 0.001)]
        - 80% of people get max_uses=1 (no reuse)
        - 10% of people get max_uses uniformly in [1..2]
        - 5% of people get max_uses uniformly in [1..5]
        - ... and so on, creating a realistic long tail.
        """
        rand_val = rng.random()
        cumulative = 0.0
        for max_count, probability in self.person_reuse_distribution:
            cumulative += probability
            if rand_val <= cumulative:
                if max_count == 1:
                    return 1  # No reuse
                return rng.randint(1, max_count)
        return 1  # fallback


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

    def __init__(
        self,
        csv_path: str,
        seed: Optional[int] = None,
        config: Optional[GeneratorConfig] = None,
    ):
        """
        Initialize the IBAN generator.

        Args:
            csv_path: Path to the Bundesbank CSV file
            seed: Optional PRNG seed for deterministic generation
            config: Optional configuration for probability distributions
        """
        self.banks: List[BankInfo] = []
        self.config = config or GeneratorConfig()
        # If no seed provided, generate one for reproducibility tracking
        if seed is None:
            import time

            seed = int(time.time() * 1000000) % (2**32)
        self.seed = seed
        # Use Python's random.Random, which implements the Mersenne Twister (MT19937) PRNG.
        # This provides high-quality, fast pseudo-random numbers suitable for simulation/testing.
        # Note: This is NOT cryptographically secure; for crypto use cases prefer secrets.SystemRandom.
        self.rng = random.Random(seed)
        # Seed Faker with the same seed to make generated personal data deterministic as well.
        self.faker = Faker("de_DE")
        self.faker.seed_instance(seed)

        # Person pool for reusability - stores base person info and their planned usage
        self.person_pool: List[
            dict
        ] = []  # List of {base_person, max_uses, current_uses, variants}

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

    def _generate_tax_id(self) -> str:
        """Generate a German Tax-ID (Steuer-ID) for natural persons.

        Format: 11 digits (different from WID)

        Returns:
            Tax-ID string
        """
        tax_id = self.rng.randint(10000000000, 99999999999)
        return str(tax_id)

    def _generate_wid(self, is_legal_entity: bool = False) -> str:
        """Generate a Wirtschafts-Identifikationsnummer (WID).

        Args:
            is_legal_entity: True for legal entities (format: DE + 9 digits, optionally '-' + 5-digit feature),
                           False for natural persons (format: DE + 10 digits, optionally '-' + 5-digit feature)

        Returns:
            WID string
        """
        if is_legal_entity:
            # Legal entities: "DE" + 9 random digits, optionally '-' + distinguishing feature (5 digits)
            # If the distinguishing feature equals 00000 (kein Unterscheidungsmerkmal), omit the suffix entirely.
            base_number = self.rng.randint(
                0, 999999999
            )  # 9 digits, allow leading zeros
            feature = self.config.get_wid_distinguishing_feature(self.rng)
            if feature == 0:
                return f"DE{base_number:09d}"
            feature_str = f"{feature:05d}"  # Pad to 5 digits
            return f"DE{base_number:09d}-{feature_str}"
        else:
            # Natural persons: "DE" + 10 random digits, optionally '-' + distinguishing feature (5 digits)
            # If the distinguishing feature equals 00000 (kein Unterscheidungsmerkmal), omit the suffix entirely.
            base_number = self.rng.randint(
                0, 9999999999
            )  # 10 digits, allow leading zeros
            feature = self.config.get_wid_distinguishing_feature(self.rng)
            if feature == 0:
                return f"DE{base_number:010d}"
            feature_str = f"{feature:05d}"  # Pad to 5 digits
            return f"DE{base_number:010d}-{feature_str}"

    def _get_or_create_person(
        self, force_economically_active: bool = False
    ) -> PersonalInfo:
        """Get an existing person from pool or create a new one, supporting reusability.

        Args:
            force_economically_active: Force person to be economically active

        Returns:
            PersonalInfo object that may be reused from pool or newly created
        """
        # Prune exhausted entries to avoid unbounded memory growth
        if self.person_pool:
            self.person_pool = [
                p for p in self.person_pool if p["current_uses"] < p["max_uses"]
            ]

        # Try to find an available person from the pool
        for person_entry in self.person_pool:
            if person_entry["current_uses"] < person_entry["max_uses"]:
                # Create a variant of this person for this use
                variant = self._create_person_variant(
                    person_entry, force_economically_active
                )
                person_entry["current_uses"] += 1
                return variant

        # No available person in pool, create new one
        return self._create_new_person_with_pool_entry(force_economically_active)

    def _create_person_variant(
        self, person_entry: dict, force_economically_active: bool = False
    ) -> PersonalInfo:
        """Create a variant of an existing person with potentially different economic activity.

        Args:
            person_entry: Person entry from the pool
            force_economically_active: Force this variant to be economically active

        Returns:
            PersonalInfo variant with same base info but potentially different economic status
        """
        base_person = person_entry["base_person"]
        is_active = self.config.should_be_economically_active(
            self.rng, force_economically_active
        )

        # Generate new WID if economically active (different business activity)
        wid = None
        if is_active:
            wid = self._generate_wid(is_legal_entity=False)

        return PersonalInfo(
            first_name=base_person.first_name,
            last_name=base_person.last_name,
            street_address=base_person.street_address,
            city=base_person.city,
            postal_code=base_person.postal_code,
            tax_id=base_person.tax_id,  # Tax-ID stays the same
            birth_date=base_person.birth_date,  # Birth date stays the same
            wid=wid,  # New WID for different economic activity
            is_economically_active=is_active,
        )

    def _create_new_person_with_pool_entry(
        self, force_economically_active: bool = False
    ) -> PersonalInfo:
        """Create a new person and add entry to pool for potential reuse.

        Args:
            force_economically_active: Force person to be economically active

        Returns:
            Newly created PersonalInfo object
        """
        # Determine how many times this person will be used
        max_uses = self.config.get_person_reuse_count(self.rng)

        # Create base person info (always create with basic Tax-ID)
        base_person = PersonalInfo(
            first_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            postal_code=self.faker.postcode(),
            tax_id=self._generate_tax_id(),
            birth_date=self.faker.date_of_birth(minimum_age=18, maximum_age=80),
            wid=None,  # Will be determined per variant
            is_economically_active=False,  # Will be determined per variant
        )

        # Add to person pool
        person_entry = {
            "base_person": base_person,
            "max_uses": max_uses,
            "current_uses": 1,  # This first use
        }
        self.person_pool.append(person_entry)

        # Create the first variant
        return self._create_person_variant(person_entry, force_economically_active)

    def _generate_personal_info(
        self, force_economically_active: bool = False
    ) -> PersonalInfo:
        """Generate personal information using Faker.

        Args:
            force_economically_active: Force person to be economically active (e.g., when legal entity is account holder)
        """
        # Use the new person pool system
        return self._get_or_create_person(force_economically_active)

    def _generate_legal_entity(self) -> LegalEntity:
        """Generate legal entity information using Faker."""
        return LegalEntity(
            name=self.faker.company(),
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            postal_code=self.faker.postcode(),
            wid=self._generate_wid(is_legal_entity=True),
        )

    def _generate_account_holders(self) -> List[AccountHolder]:
        """Generate list of account holders based on configuration."""
        # Check if it should be a legal entity (always sole holder)
        if self.config.should_be_legal_entity(self.rng):
            return [self._generate_legal_entity()]

        # Generate natural persons (not forced to be economically active as account holders)
        count = self.config.get_account_holder_count(self.rng)
        return [
            self._generate_personal_info(force_economically_active=False)
            for _ in range(count)
        ]

    def _generate_beneficiaries(
        self, has_legal_entity: bool
    ) -> List[Union[PersonalInfo, LegalEntity]]:
        """Generate list of beneficiaries. Legal entities as account holders cannot have beneficiaries."""
        if has_legal_entity:
            return []

        count = self.config.get_beneficial_owner_count(self.rng)
        beneficiaries = []
        for _ in range(count):
            # Check if this beneficiary should be a legal entity (currently 0% probability)
            if self.rng.random() < self.config.beneficiary_legal_entity_probability:
                beneficiaries.append(self._generate_legal_entity())
            else:
                # Natural person beneficiaries follow normal economic activity rules
                beneficiaries.append(
                    self._generate_personal_info(force_economically_active=False)
                )
        return beneficiaries

    def generate_iban(self) -> IBANRecord:
        """
        Generate a single valid German IBAN with account holders and beneficial owners.

        Returns:
            IBANRecord object containing IBAN, bank info, account holders, and beneficial owners
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

        # First determine if account holders will include legal entity
        will_have_legal_entity = self.config.should_be_legal_entity(self.rng)

        # Generate account holders with forced economic activity if legal entity present
        if will_have_legal_entity:
            account_holders = [self._generate_legal_entity()]
        else:
            count = self.config.get_account_holder_count(self.rng)
            # When no legal entity, natural persons follow normal economic activity rules
            account_holders = [
                self._generate_personal_info(force_economically_active=False)
                for _ in range(count)
            ]

        # Check if any account holder is a legal entity
        has_legal_entity = any(
            isinstance(holder, LegalEntity) for holder in account_holders
        )

        # Generate beneficiaries (empty if legal entity exists, otherwise with forced economic activity if legal entity account holder)
        if has_legal_entity:
            beneficiaries = []  # Legal entities cannot have beneficiaries
        else:
            count = self.config.get_beneficial_owner_count(self.rng)
            beneficiaries = []
            for _ in range(count):
                # Check if this beneficiary should be a legal entity (currently 0% probability)
                if self.rng.random() < self.config.beneficiary_legal_entity_probability:
                    beneficiaries.append(self._generate_legal_entity())
                else:
                    # Since no legal entity account holder, beneficiaries follow normal rules
                    beneficiaries.append(
                        self._generate_personal_info(force_economically_active=False)
                    )

        return IBANRecord(
            iban=iban,
            bank=bank,
            account_holders=account_holders,
            beneficiaries=beneficiaries,
        )

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
