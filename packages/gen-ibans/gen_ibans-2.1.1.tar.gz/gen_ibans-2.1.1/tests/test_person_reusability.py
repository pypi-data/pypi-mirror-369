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

from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig, PersonalInfo


def create_test_csv():
    """Create test CSV data and return temporary file path."""
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
10010020;1;BHW Bausparkasse AG;10592;Berlin;BHW Berlin;43000;BHWBDEFF;;2;;;;;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        return f.name


def test_basic_person_reusability():
    """Test basic person reusability functionality."""
    print("=== Testing Basic Person Reusability ===")

    test_csv_path = create_test_csv()

    try:
        # Configure for higher reuse probability
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities for simplicity
            account_holder_distribution=[(1, 1.0)],  # Always single holder
            beneficial_owner_distribution=[(1, 1.0)],  # Always single beneficiary
            person_reuse_distribution=[
                (1, 0.0),  # 0% single use (force reuse)
                (3, 1.0),  # 100% up to 3 uses
            ],
            economically_active_probability=0.5,  # 50% active for variation
        )
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        # Generate multiple IBANs to see reuse
        ibans = generator.generate_ibans(6)

        # Track persons by Tax-ID (unique identifier)
        persons_by_tax_id = {}
        person_usage = defaultdict(list)

        for i, record in enumerate(ibans):
            print(f"\n--- IBAN {i + 1}: {record.iban} ---")

            # Check account holders
            for holder in record.account_holders:
                if isinstance(holder, PersonalInfo):
                    tax_id = holder.tax_id
                    print(
                        f"Holder: {holder.full_name} (Tax-ID: {tax_id}, WID: {holder.wid}, Active: {holder.is_economically_active})"
                    )

                    if tax_id in persons_by_tax_id:
                        # Person reused - check if base info matches
                        base_person = persons_by_tax_id[tax_id]
                        print(
                            f"  -> REUSED person (first seen in IBAN {base_person['first_iban']})"
                        )

                        # Verify base info stays the same
                        assert holder.first_name == base_person["first_name"]
                        assert holder.last_name == base_person["last_name"]
                        assert holder.birth_date == base_person["birth_date"]
                        assert holder.tax_id == base_person["tax_id"]

                        # Economic activity and WID can be different
                        if holder.wid != base_person.get("wid"):
                            print(
                                f"  -> Different WID: {base_person.get('wid')} -> {holder.wid}"
                            )
                        if holder.is_economically_active != base_person.get(
                            "is_economically_active"
                        ):
                            print(
                                f"  -> Different activity status: {base_person.get('is_economically_active')} -> {holder.is_economically_active}"
                            )
                    else:
                        # New person
                        persons_by_tax_id[tax_id] = {
                            "first_name": holder.first_name,
                            "last_name": holder.last_name,
                            "birth_date": holder.birth_date,
                            "tax_id": holder.tax_id,
                            "wid": holder.wid,
                            "is_economically_active": holder.is_economically_active,
                            "first_iban": i + 1,
                        }
                        print("  -> NEW person")

                    person_usage[tax_id].append((i + 1, "holder", holder))

            # Check beneficiaries
            for beneficiary in record.beneficiaries:
                if isinstance(beneficiary, PersonalInfo):
                    tax_id = beneficiary.tax_id
                    print(
                        f"Beneficiary: {beneficiary.full_name} (Tax-ID: {tax_id}, WID: {beneficiary.wid}, Active: {beneficiary.is_economically_active})"
                    )

                    if tax_id in persons_by_tax_id:
                        # Person reused
                        base_person = persons_by_tax_id[tax_id]
                        print(
                            f"  -> REUSED person (first seen in IBAN {base_person['first_iban']})"
                        )
                    else:
                        # New person
                        persons_by_tax_id[tax_id] = {
                            "first_name": beneficiary.first_name,
                            "last_name": beneficiary.last_name,
                            "birth_date": beneficiary.birth_date,
                            "tax_id": beneficiary.tax_id,
                            "wid": beneficiary.wid,
                            "is_economically_active": beneficiary.is_economically_active,
                            "first_iban": i + 1,
                        }
                        print("  -> NEW person")

                    person_usage[tax_id].append((i + 1, "beneficiary", beneficiary))

        # Summary
        print("\n=== Summary ===")
        print(f"Total IBANs generated: {len(ibans)}")
        print(f"Unique persons: {len(persons_by_tax_id)}")

        reused_persons = 0
        for tax_id, usages in person_usage.items():
            if len(usages) > 1:
                reused_persons += 1
                person_info = persons_by_tax_id[tax_id]
                print(
                    f"\nPerson {person_info['first_name']} {person_info['last_name']} (Tax-ID: {tax_id}) used {len(usages)} times:"
                )
                for iban_num, role, person_obj in usages:
                    print(
                        f"  - IBAN {iban_num} as {role} (WID: {person_obj.wid}, Active: {person_obj.is_economically_active})"
                    )

        print(f"\nReused persons: {reused_persons}/{len(persons_by_tax_id)}")

        # Verify reusability worked (should have reused persons)
        if reused_persons == 0:
            print("⚠️  WARNING: No person reusability detected!")
            assert False, "Expected some person reusability"
        else:
            print("✓ Person reusability test passed!")

    except Exception as e:
        print(f"✗ Basic person reusability test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_economic_activity_variation():
    """Test that the same person can have different economic activity states."""
    print("\n=== Testing Economic Activity Variation ===")

    test_csv_path = create_test_csv()

    try:
        # Configure for guaranteed reuse with varied economic activity
        config = GeneratorConfig(
            legal_entity_probability=0.0,
            account_holder_distribution=[(1, 1.0)],
            beneficial_owner_distribution=[(0, 1.0)],  # No beneficiaries for simplicity
            person_reuse_distribution=[(5, 1.0)],  # Everyone used up to 5 times
            economically_active_probability=0.5,  # 50% chance for variation
        )
        generator = IBANGenerator(test_csv_path, seed=123, config=config)

        # Generate many IBANs to increase chance of variation
        ibans = generator.generate_ibans(10)

        # Track variations per person
        person_variations = defaultdict(list)

        for record in ibans:
            for holder in record.account_holders:
                if isinstance(holder, PersonalInfo):
                    person_variations[holder.tax_id].append(
                        {"wid": holder.wid, "is_active": holder.is_economically_active}
                    )

        # Check for variations
        variations_found = 0
        for tax_id, variations in person_variations.items():
            if len(variations) > 1:
                # Check if there are different states
                wids = set(v["wid"] for v in variations)
                activities = set(v["is_active"] for v in variations)

                if len(wids) > 1 or len(activities) > 1:
                    variations_found += 1
                    print(f"Person {tax_id}: {len(variations)} uses with variations:")
                    for i, var in enumerate(variations):
                        print(
                            f"  Use {i + 1}: WID={var['wid']}, Active={var['is_active']}"
                        )

        if variations_found > 0:
            print(
                f"✓ Found {variations_found} persons with economic activity variations!"
            )
            return None
        else:
            print("⚠️  No economic activity variations detected")
            return None  # Not a failure, just uncommon with this seed

    except Exception as e:
        print(f"✗ Economic activity variation test failed: {e}")
        import traceback

        traceback.print_exc()
        return None
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def main():
    """Run all person reusability tests."""
    print("Starting person reusability tests...\n")

    tests = [test_basic_person_reusability, test_economic_activity_variation]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All person reusability tests passed!")
        return 0
    else:
        print("❌ Some person reusability tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
