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
from datetime import date


def create_test_csv():
    """Create test CSV data and return temporary file path."""
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        return f.name


def test_birth_date_generation():
    """Test that birth dates are generated for natural persons."""
    print("=== Testing Birth Date Generation ===")

    test_csv_path = create_test_csv()

    try:
        # Test with natural persons only
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            account_holder_distribution=[(1, 1.0)],  # Always single holder
        )
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        ibans = generator.generate_ibans(5)

        for i, record in enumerate(ibans, 1):
            holder = record.account_holders[0]
            print(f"\nAccount {i}: {holder.full_name}")
            print(f"  Birth Date: {holder.birth_date}")
            print(f"  Type: {type(holder.birth_date)}")

            # Verify birth_date is present and is a date object
            assert hasattr(holder, "birth_date"), (
                f"Birth date missing for {holder.full_name}"
            )
            assert holder.birth_date is not None, (
                f"Birth date is None for {holder.full_name}"
            )
            assert isinstance(holder.birth_date, date), (
                f"Birth date is not a date object for {holder.full_name}: {type(holder.birth_date)}"
            )

            # Verify birth date is reasonable (between 18 and 80 years old)
            today = date.today()
            age = (
                today.year
                - holder.birth_date.year
                - (
                    (today.month, today.day)
                    < (holder.birth_date.month, holder.birth_date.day)
                )
            )
            assert 18 <= age <= 80, (
                f"Birth date age {age} is not in reasonable range for {holder.full_name}"
            )

        print("✓ Birth date generation test passed!")

    except Exception as e:
        print(f"✗ Birth date generation test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_legal_entity_no_birth_date():
    """Test that legal entities do not have birth dates."""
    print("\n=== Testing Legal Entity No Birth Date ===")

    test_csv_path = create_test_csv()

    try:
        # Test with legal entities only
        config = GeneratorConfig(
            legal_entity_probability=1.0,  # Only legal entities
        )
        generator = IBANGenerator(test_csv_path, seed=123, config=config)

        ibans = generator.generate_ibans(3)

        for i, record in enumerate(ibans, 1):
            holder = record.account_holders[0]
            print(f"\nAccount {i}: {holder.name} (Legal Entity)")

            # Verify it's a legal entity and doesn't have birth_date
            assert isinstance(holder, LegalEntity), (
                f"Expected legal entity, got {type(holder)}"
            )
            assert not hasattr(holder, "birth_date"), (
                "Legal entity should not have birth_date"
            )

        print("✓ Legal entity no birth date test passed!")

    except Exception as e:
        print(f"✗ Legal entity no birth date test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def test_birth_date_in_output():
    """Test that birth dates appear in various output formats."""
    print("\n=== Testing Birth Date in Output Formats ===")

    test_csv_path = create_test_csv()

    try:
        from gen_ibans.cli import OutputFormatter

        # Test with natural persons
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities
            account_holder_distribution=[(1, 1.0)],  # Always single holder
        )
        generator = IBANGenerator(test_csv_path, seed=456, config=config)

        ibans = generator.generate_ibans(2)

        # Test stdout formatter
        print("\nTesting stdout formatter:")
        from io import StringIO
        import contextlib

        with contextlib.redirect_stdout(StringIO()) as f:
            OutputFormatter.format_stdout(
                ibans, include_bank_info=True, include_personal_info=True
            )
        stdout_output = f.getvalue()

        # Check that birth date appears in output
        for record in ibans:
            holder = record.account_holders[0]
            assert f"Born: {holder.birth_date}" in stdout_output, (
                f"Birth date not found in stdout output for {holder.full_name}"
            )

        print("Stdout output contains birth dates ✓")

        # Test CSV formatter
        csv_path = tempfile.mktemp(suffix=".csv")
        try:
            OutputFormatter.format_csv(ibans, csv_path, clean=True)
            with open(csv_path, "r", encoding="utf-8") as f:
                csv_content = f.read()

            for record in ibans:
                holder = record.account_holders[0]
                assert f"Born: {holder.birth_date}" in csv_content, (
                    f"Birth date not found in CSV output for {holder.full_name}"
                )

            print("CSV output contains birth dates ✓")
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)

        # Test XML formatter
        xml_path = tempfile.mktemp(suffix=".xml")
        try:
            OutputFormatter.format_xml(ibans, xml_path, clean=True)
            with open(xml_path, "r", encoding="utf-8") as f:
                xml_content = f.read()

            for record in ibans:
                holder = record.account_holders[0]
                assert f"<birth_date>{holder.birth_date}</birth_date>" in xml_content, (
                    f"Birth date element not found in XML output for {holder.full_name}"
                )

            print("XML output contains birth date elements ✓")
        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)

        # Test JSON formatter
        json_path = tempfile.mktemp(suffix=".json")
        try:
            OutputFormatter.format_json(ibans, json_path, clean=True)
            with open(json_path, "r", encoding="utf-8") as f:
                json_content = f.read()

            for record in ibans:
                holder = record.account_holders[0]
                assert f'"birth_date": "{holder.birth_date}"' in json_content, (
                    f"Birth date field not found in JSON output for {holder.full_name}"
                )

            print("JSON output contains birth date fields ✓")
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)

        print("✓ Birth date in output formats test passed!")

    except Exception as e:
        print(f"✗ Birth date in output formats test failed: {e}")
        import traceback

        traceback.print_exc()
        pass
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


def main():
    """Run all birth date tests."""
    print("Starting birth date functionality tests...\n")

    tests = [
        test_birth_date_generation,
        test_legal_entity_no_birth_date,
        test_birth_date_in_output,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All birth date tests passed!")
        return 0
    else:
        print("❌ Some birth date tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
