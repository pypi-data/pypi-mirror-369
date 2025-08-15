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
from gen_ibans.iban_generator import IBANGenerator, GeneratorConfig, LegalEntity


def test_wid_generation():
    """Test WID generation for natural persons and legal entities."""

    # Create test CSV data
    test_csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl
10010010;1;Postbank Ndl der DB Privat- und Firmenkundenbank;10115;Berlin;Postbank Berlin;52011;PBNKDEFF;;1;;;;;
"""

    # Write test data to temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv_content)
        test_csv_path = f.name

    try:
        # Test with default configuration
        config = GeneratorConfig(
            legal_entity_probability=0.5
        )  # 50% legal entities for testing
        generator = IBANGenerator(test_csv_path, seed=42, config=config)

        print("=== Testing WID Generation ===")

        # Generate some IBANs
        ibans = generator.generate_ibans(5)

        for i, record in enumerate(ibans, 1):
            print(f"\nIBAN {i}: {record.iban}")
            print(f"Account Holders ({len(record.account_holders)}):")
            for j, holder in enumerate(record.account_holders, 1):
                if isinstance(holder, LegalEntity):
                    print(f"  {j}. {holder.name} (Legal Entity)")
                    print(f"     WID: {holder.wid}")
                    # Verify WID format for legal entities: "DE" + 9 digits
                    if not (
                        holder.wid.startswith("DE")
                        and len(holder.wid) == 11
                        and holder.wid[2:].isdigit()
                    ):
                        print(
                            f"     ERROR: Invalid WID format for legal entity: {holder.wid}"
                        )
                else:
                    print(f"  {j}. {holder.full_name}")
                    print(f"     WID: {holder.wid}")
                    # Verify WID format for natural persons: 11 digits
                    if not (len(holder.wid) == 11 and holder.wid.isdigit()):
                        print(
                            f"     ERROR: Invalid WID format for natural person: {holder.wid}"
                        )

            print(f"Beneficiaries ({len(record.beneficiaries)}):")
            if record.beneficiaries:
                for j, beneficiary in enumerate(record.beneficiaries, 1):
                    if isinstance(beneficiary, LegalEntity):
                        print(f"  {j}. {beneficiary.name} (Legal Entity)")
                        print(f"     WID: {beneficiary.wid}")
                    else:
                        print(f"  {j}. {beneficiary.full_name}")
                        print(f"     WID: {beneficiary.wid}")
            else:
                print("  None")

        print("\n✓ WID generation test completed!")

    except Exception as e:
        print(f"✗ WID generation test failed: {e}")
        import traceback

        traceback.print_exc()
        pass
    finally:
        # Clean up
        if os.path.exists(test_csv_path):
            os.unlink(test_csv_path)


if __name__ == "__main__":
    test_wid_generation()
