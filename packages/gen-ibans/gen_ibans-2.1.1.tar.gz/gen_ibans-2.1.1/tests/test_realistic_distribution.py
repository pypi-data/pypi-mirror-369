#!/usr/bin/env python3
"""
MIT License

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

import sys
import os
import tempfile
from collections import defaultdict

# Add the gen_ibans module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "gen_ibans"))

from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig


def create_test_csv():
    """Create test CSV data and return temporary file path."""
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
10010020;1;BHW Bausparkasse AG;10592;Berlin;BHW Berlin;43000;BHWBDEFF;;2;;;;;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        return f.name


def test_realistic_distribution():
    """Test that the new distribution produces realistic patterns."""
    print("=== Testing Realistic Person Reuse Distribution ===")

    test_csv_path = create_test_csv()

    try:
        # Use default configuration with new realistic distribution
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            account_holder_distribution=[(1, 1.0)],  # Always single holder
            beneficial_owner_distribution=[(0, 1.0)],  # No beneficiaries for simplicity
        )
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        # Generate many IBANs to get good statistical distribution
        ibans = generator.generate_ibans(1000)

        # Track how many accounts each person has
        person_account_count = defaultdict(int)

        for record in ibans:
            for holder in record.account_holders:
                if hasattr(holder, "tax_id"):  # Natural person
                    person_account_count[holder.tax_id] += 1

        # Analyze the distribution
        account_counts = defaultdict(int)
        for tax_id, count in person_account_count.items():
            account_counts[count] += 1

        total_persons = len(person_account_count)

        print(f"Total persons generated: {total_persons}")
        print(f"Total IBANs generated: {len(ibans)}")
        print("\nAccount ownership distribution:")

        # Show distribution in ranges matching our configuration
        ranges = [
            (1, 1, "1 account"),
            (2, 2, "2 accounts"),
            (3, 5, "3-5 accounts"),
            (6, 15, "6-15 accounts"),
            (16, 50, "16-50 accounts"),
            (51, 200, "51-200 accounts"),
        ]

        for min_val, max_val, label in ranges:
            count = sum(account_counts[i] for i in range(min_val, max_val + 1))
            percentage = (count / total_persons) * 100 if total_persons > 0 else 0
            print(f"  {label}: {count} persons ({percentage:.1f}%)")

        # Check that 1-2 accounts is the majority (should be ~85%)
        one_or_two_accounts = account_counts[1] + account_counts[2]
        one_or_two_percentage = (one_or_two_accounts / total_persons) * 100

        print("\nRealistic check:")
        print(
            f"Persons with 1-2 accounts: {one_or_two_accounts}/{total_persons} ({one_or_two_percentage:.1f}%)"
        )

        if one_or_two_percentage >= 75:  # Should be around 85%, allow some variance
            print("✓ Distribution looks realistic! Most people have 1-2 accounts.")
        else:
            print(
                f"✗ Distribution doesn't look realistic. Expected ~85% with 1-2 accounts, got {one_or_two_percentage:.1f}%"
            )
            assert False, "Distribution check failed"

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def main():
    """Run the realistic distribution test."""
    print("Starting realistic person reuse distribution test...\n")

    if test_realistic_distribution():
        print("\n🎉 Realistic distribution test passed!")
        return 0
    else:
        print("\n❌ Realistic distribution test failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
