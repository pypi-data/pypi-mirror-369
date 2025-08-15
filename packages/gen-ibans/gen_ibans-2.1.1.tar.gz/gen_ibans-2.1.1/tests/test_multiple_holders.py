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

import tempfile
import os
import json
from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig
from gen_ibans.cli import OutputFormatter


def create_test_csv():
    """Create test CSV data and return temporary file path."""
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        return f.name


def test_multiple_formats():
    """Test how multiple holders and beneficiaries are displayed in different formats."""
    print("=== Testing Multiple Holders and Beneficiaries Output Formats ===")

    test_csv_path = create_test_csv()

    try:
        # Force multiple holders and beneficiaries
        config = GeneratorConfig(
            legal_entity_probability=0.0,  # No legal entities for simplicity
            account_holder_distribution=[(3, 1.0)],  # Always 3 holders
            beneficial_owner_distribution=[(2, 1.0)],  # Always 2 beneficiaries
        )
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        ibans = generator.generate_ibans(1)
        record = ibans[0]

        print(
            f"Generated record with {len(record.account_holders)} holders and {len(record.beneficiaries)} beneficiaries"
        )

        # Test TXT format
        print("\n--- TXT Format ---")
        txt_path = tempfile.mktemp(suffix=".txt")
        try:
            OutputFormatter.format_txt(ibans, txt_path, clean=True)
            with open(txt_path, "r", encoding="utf-8") as f:
                txt_content = f.read()
            print("TXT Output:")
            print(txt_content.strip())
        finally:
            if os.path.exists(txt_path):
                os.unlink(txt_path)

        # Test CSV format
        print("\n--- CSV Format ---")
        csv_path = tempfile.mktemp(suffix=".csv")
        try:
            OutputFormatter.format_csv(ibans, csv_path, clean=True)
            with open(csv_path, "r", encoding="utf-8") as f:
                csv_content = f.read()
            print("CSV Output:")
            print(csv_content.strip())
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)

        # Test JSON format
        print("\n--- JSON Format ---")
        json_path = tempfile.mktemp(suffix=".json")
        try:
            OutputFormatter.format_json(ibans, json_path, clean=True)
            with open(json_path, "r", encoding="utf-8") as f:
                json_content = f.read()
            print("JSON Output (formatted):")
            data = json.loads(json_content)
            print(json.dumps(data, indent=2))
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


if __name__ == "__main__":
    test_multiple_formats()
