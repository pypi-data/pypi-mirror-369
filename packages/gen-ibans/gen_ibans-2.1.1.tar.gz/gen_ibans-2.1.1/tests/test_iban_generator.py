"""
Tests for the IBAN Generator module.

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

import unittest
import tempfile
import os

from gen_ibans.iban_generator import IBANGenerator, BankInfo, validate_iban


class TestBankInfo(unittest.TestCase):
    """Test BankInfo class."""

    def test_bank_info_creation(self):
        """Test BankInfo object creation."""
        bank = BankInfo("12345678", "DEUTDEBBXXX", "Deutsche Bank")
        self.assertEqual(bank.bankleitzahl, "12345678")
        self.assertEqual(bank.bic, "DEUTDEBBXXX")
        self.assertEqual(bank.name, "Deutsche Bank")

    def test_bank_info_repr(self):
        """Test BankInfo string representation."""
        bank = BankInfo("12345678", "DEUTDEBBXXX", "Deutsche Bank")
        expected = "BankInfo(blz=12345678, bic=DEUTDEBBXXX, name=Deutsche Bank)"
        self.assertEqual(repr(bank), expected)


class TestIBANValidation(unittest.TestCase):
    """Test IBAN validation functionality."""

    def test_valid_iban(self):
        """Test validation of valid IBANs."""
        # Known valid German IBAN
        self.assertTrue(validate_iban("DE89370400440532013000"))
        self.assertTrue(validate_iban("DE02120300000000202051"))

    def test_invalid_iban_format(self):
        """Test validation of invalid IBAN formats."""
        # Wrong length
        self.assertFalse(validate_iban("DE8937040044053201300"))  # 21 chars
        self.assertFalse(validate_iban("DE893704004405320130000"))  # 23 chars

        # Wrong country code
        self.assertFalse(validate_iban("FR89370400440532013000"))

        # Empty or None
        self.assertFalse(validate_iban(""))
        self.assertFalse(validate_iban(None))

        # Non-numeric parts
        self.assertFalse(validate_iban("DExx370400440532013000"))
        self.assertFalse(validate_iban("DE89370400440532013xxx"))

    def test_invalid_iban_checksum(self):
        """Test validation of IBANs with invalid checksums."""
        # Change last digit of valid IBAN
        self.assertFalse(validate_iban("DE89370400440532013001"))
        # Change check digits
        self.assertFalse(validate_iban("DE88370400440532013000"))


class TestIBANGenerator(unittest.TestCase):
    """Test IBANGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a sample CSV content
        self.csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfzifferberechnungsmethode;Datensatznummer;Änderungskennzeichen;Bankleitzahllöschung;Nachfolge-Bankleitzahl
"10000000";"1";"Bundesbank";"10591";"Berlin";"BBk Berlin";"20100";"MARKDEF1100";"09";"011380";"U";"0";"00000000"
"10010010";"1";"Postbank";"10559";"Berlin";"Postbank Berlin";"10010";"PBNKDEFFXXX";"24";"000538";"U";"0";"00000000"
"37040044";"1";"Commerzbank";"50667";"Köln";"Commerzbank Köln";"24100";"COBADEFFXXX";"13";"024463";"U";"0";"00000000"
"""

        # Create temporary CSV file
        self.temp_csv = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        )
        self.temp_csv.write(self.csv_content)
        self.temp_csv.close()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)

    def test_load_banks_success(self):
        """Test successful loading of banks from CSV."""
        generator = IBANGenerator(self.temp_csv.name)
        self.assertEqual(len(generator.banks), 3)

        # Check first bank
        bank = generator.banks[0]
        self.assertEqual(bank.bankleitzahl, "10000000")
        self.assertEqual(bank.bic, "MARKDEF1100")
        self.assertEqual(bank.name, "Bundesbank")

    def test_load_banks_file_not_found(self):
        """Test error handling for missing CSV file."""
        with self.assertRaises(ValueError) as context:
            IBANGenerator("nonexistent.csv")
        self.assertIn("Error loading CSV file", str(context.exception))

    def test_generate_single_iban(self):
        """Test generation of a single IBAN."""
        generator = IBANGenerator(self.temp_csv.name, seed=12345)
        iban_record = generator.generate_iban()

        # Check IBAN format
        self.assertEqual(len(iban_record.iban), 22)
        self.assertTrue(iban_record.iban.startswith("DE"))
        self.assertTrue(validate_iban(iban_record.iban))

        # Check bank info
        self.assertIsInstance(iban_record.bank, BankInfo)
        self.assertIn(iban_record.bank.bankleitzahl, iban_record.iban)

    def test_generate_multiple_ibans(self):
        """Test generation of multiple IBANs."""
        generator = IBANGenerator(self.temp_csv.name, seed=12345)
        ibans = generator.generate_ibans(5)

        self.assertEqual(len(ibans), 5)

        for iban_record in ibans:
            self.assertEqual(len(iban_record.iban), 22)
            self.assertTrue(iban_record.iban.startswith("DE"))
            self.assertTrue(validate_iban(iban_record.iban))
            self.assertIsInstance(iban_record.bank, BankInfo)

    def test_deterministic_generation(self):
        """Test that same seed produces same results."""
        generator1 = IBANGenerator(self.temp_csv.name, seed=42)
        generator2 = IBANGenerator(self.temp_csv.name, seed=42)

        ibans1 = generator1.generate_ibans(3)
        ibans2 = generator2.generate_ibans(3)

        # Should produce identical results
        for iban_record1, iban_record2 in zip(ibans1, ibans2):
            self.assertEqual(iban_record1.iban, iban_record2.iban)
            self.assertEqual(
                iban_record1.bank.bankleitzahl, iban_record2.bank.bankleitzahl
            )

    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results."""
        generator1 = IBANGenerator(self.temp_csv.name, seed=42)
        generator2 = IBANGenerator(self.temp_csv.name, seed=24)

        ibans1 = generator1.generate_ibans(10)
        ibans2 = generator2.generate_ibans(10)

        # Should produce different results (very high probability)
        iban_strings1 = [iban_record.iban for iban_record in ibans1]
        iban_strings2 = [iban_record.iban for iban_record in ibans2]
        self.assertNotEqual(iban_strings1, iban_strings2)

    def test_invalid_count(self):
        """Test error handling for invalid count values."""
        generator = IBANGenerator(self.temp_csv.name)

        with self.assertRaises(ValueError):
            generator.generate_ibans(0)

        with self.assertRaises(ValueError):
            generator.generate_ibans(-1)

    def test_no_banks_loaded(self):
        """Test error handling when no banks are loaded."""
        # Create CSV with no valid banks (missing BIC)
        csv_content_no_bic = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfzifferberechnungsmethode;Datensatznummer;Änderungskennzeichen;Bankleitzahllöschung;Nachfolge-Bankleitzahl
"10000000";"1";"Bundesbank";"10591";"Berlin";"BBk Berlin";"20100";"";"09";"011380";"U";"0";"00000000"
"""

        temp_csv_no_bic = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        )
        temp_csv_no_bic.write(csv_content_no_bic)
        temp_csv_no_bic.close()

        try:
            generator = IBANGenerator(temp_csv_no_bic.name)
            with self.assertRaises(ValueError) as context:
                generator.generate_iban()
            self.assertIn("No valid banks loaded", str(context.exception))
        finally:
            os.unlink(temp_csv_no_bic.name)

    def test_check_digit_calculation(self):
        """Test IBAN check digit calculation."""
        generator = IBANGenerator(self.temp_csv.name)

        # Test with known values
        check_digits = generator._calculate_iban_check_digits("37040044", "0532013000")
        self.assertEqual(check_digits, "89")  # Known result for DE89370400440532013000

    def test_account_number_generation(self):
        """Test account number generation."""
        generator = IBANGenerator(self.temp_csv.name, seed=12345)

        account_nums = [generator._generate_account_number() for _ in range(10)]

        # Check format (10 digits, no leading zeros in generated number)
        for acc_num in account_nums:
            self.assertEqual(len(acc_num), 10)
            self.assertTrue(acc_num.isdigit())
            # Should not be all zeros
            self.assertNotEqual(acc_num, "0000000000")

    def test_get_bank_count(self):
        """Test bank count method."""
        generator = IBANGenerator(self.temp_csv.name)
        self.assertEqual(generator.get_bank_count(), 3)


if __name__ == "__main__":
    unittest.main()
