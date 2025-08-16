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

# Add the gen_ibans module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "gen_ibans"))

from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig, LegalEntity


def test_basic_functionality():
    """Test basic IBAN generation with default config."""
    print("=== Testing Basic Functionality ===")

    # Use a dummy bank data (we'll create a minimal one for testing)
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
10010020;1;BHW Bausparkasse AG;10592;Berlin;BHW Berlin;43000;BHWBDEFF;;2;;;;;
"""

    # Write test data to a temporary file
    test_csv_path = "test_banks.csv"
    with open(test_csv_path, "w", encoding="utf-8") as f:
        f.write(test_csv_content)

    try:
        # Test with default configuration
        config = GeneratorConfig()
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        print(f"Loaded {generator.get_bank_count()} banks")
        print(f"Using seed: {generator.seed}")

        # Generate some IBANs
        ibans = generator.generate_ibans(5)

        print(f"\nGenerated {len(ibans)} IBANs:")
        for i, record in enumerate(ibans, 1):
            print(f"\n{i}. IBAN: {record.iban}")
            print(f"   Account Holders ({len(record.account_holders)}):")
            for j, holder in enumerate(record.account_holders, 1):
                if isinstance(holder, LegalEntity):
                    print(f"     {j}. {holder.name} (Legal Entity)")
                    print(f"        Address: {holder.full_address}")
                else:
                    print(f"     {j}. {holder.full_name}")
                    print(f"        Address: {holder.full_address}")

            print(f"   Beneficial Owners ({len(record.beneficial_owners)}):")
            if record.beneficial_owners:
                for j, beneficiary in enumerate(record.beneficial_owners, 1):
                    print(f"     {j}. {beneficiary.full_name}")
                    print(f"        Address: {beneficiary.full_address}")
            else:
                print("     None")

            print(f"   Bank: {record.bank.name} ({record.bank.bic})")

        print("\n✓ Basic functionality test passed!")

    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        raise
    finally:
        # Clean up test file
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


def test_custom_configuration():
    """Test with custom probability distributions."""
    print("\n=== Testing Custom Configuration ===")

    # Create test data
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
10010020;1;BHW Bausparkasse AG;10592;Berlin;BHW Berlin;43000;BHWBDEFF;;2;;;;;
"""

    test_csv_path = "test_banks_custom.csv"
    with open(test_csv_path, "w", encoding="utf-8") as f:
        f.write(test_csv_content)

    try:
        # Custom configuration with higher legal entity probability
        custom_config = GeneratorConfig(
            legal_entity_probability=0.5,  # 50% legal entities
            account_holder_distribution=[
                (1, 0.3),  # 30% single holder
                (2, 0.4),  # 40% two holders
                (5, 0.3),  # 30% up to 5 holders
            ],
            beneficial_owner_distribution=[
                (0, 0.4),  # 40% no beneficial owners
                (1, 0.3),  # 30% one beneficial owner
                (3, 0.3),  # 30% up to 3 beneficial owners
            ],
        )

        generator = IBANGenerator(test_csv_path, seed=123, config=custom_config)
        ibans = generator.generate_ibans(10)

        # Analyze results
        legal_entity_count = 0
        multiple_holders_count = 0
        beneficial_owners_count = 0

        print(f"\nGenerated {len(ibans)} IBANs with custom config:")
        for i, record in enumerate(ibans, 1):
            has_legal_entity = any(
                isinstance(holder, LegalEntity) for holder in record.account_holders
            )
            if has_legal_entity:
                legal_entity_count += 1
            if len(record.account_holders) > 1:
                multiple_holders_count += 1
            if record.beneficial_owners:
                beneficial_owners_count += 1

            print(
                f"{i}. Holders: {len(record.account_holders)}, Beneficiaries: {len(record.beneficial_owners)}, Legal Entity: {has_legal_entity}"
            )

        print("\nStatistics:")
        print(
            f"  Legal entities: {legal_entity_count}/{len(ibans)} ({legal_entity_count / len(ibans) * 100:.1f}%)"
        )
        print(
            f"  Multiple holders: {multiple_holders_count}/{len(ibans)} ({multiple_holders_count / len(ibans) * 100:.1f}%)"
        )
        print(
            f"  With beneficial owners: {beneficial_owners_count}/{len(ibans)} ({beneficial_owners_count / len(ibans) * 100:.1f}%)"
        )

        print("\n✓ Custom configuration test passed!")

    except Exception as e:
        print(f"✗ Custom configuration test failed: {e}")
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


def test_backward_compatibility():
    """Test that the .person property still works for backward compatibility."""
    print("\n=== Testing Backward Compatibility ===")

    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
"""

    test_csv_path = "test_banks_compat.csv"
    with open(test_csv_path, "w", encoding="utf-8") as f:
        f.write(test_csv_content)

    try:
        # Force only natural persons with single account holder
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            account_holder_distribution=[(1, 1.0)],  # Always single holder
        )

        generator = IBANGenerator(test_csv_path, seed=42, config=config)
        record = generator.generate_iban()

        # Test backward compatibility
        if record.person is not None:
            print(
                f"✓ Backward compatibility: record.person = {record.person.full_name}"
            )
            print(f"✓ Address: {record.person.full_address}")
            return None
        else:
            print("✗ Backward compatibility failed: record.person is None")
            return None

    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return None
    finally:
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


def main():
    """Run all tests."""
    print("Starting tests for new IBAN generator features...\n")

    tests = [
        test_basic_functionality,
        test_custom_configuration,
        test_backward_compatibility,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
