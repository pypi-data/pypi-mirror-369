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

# Add the gen_ibans module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "gen_ibans"))

from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig, LegalEntity


def create_test_csv():
    """Create test CSV data and return temporary file path."""
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
10010020;1;BHW Bausparkasse AG;10592;Berlin;BHW Berlin;43000;BHWBDEFF;;2;;;;;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        return f.name


def test_basic_id_system():
    """Test basic Tax-ID and WID generation."""
    print("=== Testing Basic ID System ===")

    test_csv_path = create_test_csv()

    try:
        # Test with natural persons only and mixed economic activity
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            economically_active_probability=0.5,  # 50% active for easy testing
            account_holder_distribution=[(1, 1.0)],  # Always single holder
        )
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        ibans = generator.generate_ibans(10)

        economically_active_count = 0
        non_active_count = 0

        for i, record in enumerate(ibans, 1):
            holder = record.account_holders[0]
            print(f"\nAccount {i}: {holder.full_name}")
            print(f"  Tax-ID: {holder.tax_id}")
            print(f"  WID: {holder.wid}")
            print(f"  Economically Active: {holder.is_economically_active}")

            # Verify Tax-ID is always present and has correct format
            assert holder.tax_id is not None, f"Tax-ID missing for {holder.full_name}"
            assert len(holder.tax_id) == 11, (
                f"Tax-ID wrong length for {holder.full_name}: {holder.tax_id}"
            )
            assert holder.tax_id.isdigit(), (
                f"Tax-ID not numeric for {holder.full_name}: {holder.tax_id}"
            )

            # Verify WID presence matches economic activity
            if holder.is_economically_active:
                assert holder.wid is not None, (
                    f"WID missing for economically active {holder.full_name}"
                )
                assert holder.wid.startswith("DE"), (
                    f"WID wrong format for {holder.full_name}: {holder.wid}"
                )
                assert len(holder.wid) == 13, (
                    f"WID wrong length for {holder.full_name}: {holder.wid}"
                )
                economically_active_count += 1
            else:
                assert holder.wid is None, (
                    f"WID present for non-active {holder.full_name}: {holder.wid}"
                )
                non_active_count += 1

        print(
            f"\nResults: {economically_active_count} active, {non_active_count} non-active"
        )
        print("✓ Basic ID system test passed!")

    except Exception as e:
        print(f"✗ Basic ID system test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_wid_feature_distribution():
    """Test WID distinguishing feature distribution."""
    print("\n=== Testing WID Feature Distribution ===")

    test_csv_path = create_test_csv()

    try:
        # Test with all economically active to get WIDs
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            economically_active_probability=1.0,  # All active
            account_holder_distribution=[(1, 1.0)],  # Always single holder
            wid_feature_distribution=[
                (1, 0.5),  # 50% get 00001 for easy testing
                (10, 0.3),  # 30% get 00002-00010
                (100, 0.15),  # 15% get 00011-00100
                (99999, 0.05),  # 5% get 00101-99999
            ],
        )
        generator = IBANGenerator(test_csv_path, seed=123, config=config)

        ibans = generator.generate_ibans(20)

        feature_counts = {1: 0, 10: 0, 100: 0, 99999: 0}

        for record in ibans:
            holder = record.account_holders[0]
            wid = holder.wid

            # Extract feature from WID (positions 2-6, 5 digits)
            feature_str = wid[2:7]
            feature = int(feature_str)

            print(f"{holder.full_name}: WID {wid}, Feature: {feature:05d}")

            if feature == 1:
                feature_counts[1] += 1
            elif 2 <= feature <= 10:
                feature_counts[10] += 1
            elif 11 <= feature <= 100:
                feature_counts[100] += 1
            elif 101 <= feature <= 99999:
                feature_counts[99999] += 1

        print("\nFeature distribution:")
        print(f"  00001: {feature_counts[1]} ({feature_counts[1] / 20 * 100:.1f}%)")
        print(
            f"  00002-00010: {feature_counts[10]} ({feature_counts[10] / 20 * 100:.1f}%)"
        )
        print(
            f"  00011-00100: {feature_counts[100]} ({feature_counts[100] / 20 * 100:.1f}%)"
        )
        print(
            f"  00101-99999: {feature_counts[99999]} ({feature_counts[99999] / 20 * 100:.1f}%)"
        )

        print("✓ WID feature distribution test passed!")

    except Exception as e:
        print(f"✗ WID feature distribution test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_legal_entity_forcing():
    """Test that legal entity account holders don't change natural person behavior (since legal entities are sole holders)."""
    print("\n=== Testing Legal Entity Account Holders ===")

    test_csv_path = create_test_csv()

    try:
        # Test with legal entities
        config = GeneratorConfig(
            legal_entity_probability=1.0,  # Always legal entities
            economically_active_probability=0.2,  # 20% for natural persons (not relevant here)
            beneficial_owner_distribution=[(0, 1.0)],  # No beneficiaries
        )
        generator = IBANGenerator(test_csv_path, seed=456, config=config)

        ibans = generator.generate_ibans(5)

        for i, record in enumerate(ibans, 1):
            print(f"\nAccount {i}:")
            assert len(record.account_holders) == 1, (
                "Legal entity should be sole holder"
            )

            holder = record.account_holders[0]
            assert isinstance(holder, LegalEntity), (
                "Account holder should be legal entity"
            )
            print(f"  Legal Entity: {holder.name}")
            print(f"  WID: {holder.wid}")

            # Verify legal entity WID format
            assert holder.wid.startswith("DE"), (
                f"Legal entity WID wrong format: {holder.wid}"
            )
            assert len(holder.wid) == 11, f"Legal entity WID wrong length: {holder.wid}"

            # Legal entities cannot have beneficiaries
            assert len(record.beneficiaries) == 0, (
                "Legal entity should not have beneficiaries"
            )

        print("✓ Legal entity forcing test passed!")

    except Exception as e:
        print(f"✗ Legal entity forcing test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_mixed_scenarios():
    """Test mixed scenarios with various configurations."""
    print("\n=== Testing Mixed Scenarios ===")

    test_csv_path = create_test_csv()

    try:
        # Test with default configuration
        config = GeneratorConfig()  # Use defaults
        generator = IBANGenerator(test_csv_path, seed=789, config=config)

        ibans = generator.generate_ibans(10)

        natural_person_count = 0
        legal_entity_count = 0
        economically_active_count = 0
        beneficiary_count = 0

        for record in ibans:
            print(f"\nIBAN: {record.iban}")

            # Count account holder types
            for holder in record.account_holders:
                if isinstance(holder, LegalEntity):
                    legal_entity_count += 1
                    print(f"  Legal Entity Holder: {holder.name} (WID: {holder.wid})")
                else:
                    natural_person_count += 1
                    if holder.is_economically_active:
                        economically_active_count += 1
                    print(
                        f"  Natural Person Holder: {holder.full_name} (Tax-ID: {holder.tax_id}, WID: {holder.wid}, Active: {holder.is_economically_active})"
                    )

            # Count beneficiaries
            for beneficiary in record.beneficiaries:
                beneficiary_count += 1
                if isinstance(beneficiary, LegalEntity):
                    print(
                        f"  Legal Entity Beneficiary: {beneficiary.name} (WID: {beneficiary.wid})"
                    )
                else:
                    print(
                        f"  Natural Person Beneficiary: {beneficiary.full_name} (Tax-ID: {beneficiary.tax_id}, WID: {beneficiary.wid}, Active: {beneficiary.is_economically_active})"
                    )

        print("\nSummary:")
        print(f"  Natural Person Holders: {natural_person_count}")
        print(f"  Legal Entity Holders: {legal_entity_count}")
        print(f"  Economically Active Natural Persons: {economically_active_count}")
        print(f"  Total Beneficiaries: {beneficiary_count}")

        print("✓ Mixed scenarios test passed!")

    except Exception as e:
        print(f"✗ Mixed scenarios test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def main():
    """Run all comprehensive tests."""
    print("Starting comprehensive tests for new ID system...\n")

    tests = [
        test_basic_id_system,
        test_wid_feature_distribution,
        test_legal_entity_forcing,
        test_mixed_scenarios,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All comprehensive tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
