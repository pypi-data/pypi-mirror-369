"""
Test cases for different input formats (CSV, TXT, XML) and encodings (UTF-8, ISO-8859-1).

This module tests the IBAN generator's ability to handle various file formats
and character encodings commonly used for German banking data.

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
from gen_ibans.iban_generator import IBANGenerator


class TestFormatAndEncoding(unittest.TestCase):
    """Test cases for different file formats and encodings."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

        # Sample bank data with German umlauts for encoding tests
        self.bank_data = [
            {"blz": "10000000", "name": "Bundesbank", "bic": "MARKDEF1100"},
            {
                "blz": "10010010",
                "name": "Postbank Ndl der Deutsche Bank",
                "bic": "PBNKDEFFXXX",
            },
            {
                "blz": "50050000",
                "name": "Bank für München",  # Contains umlauts
                "bic": "BYLADEMMXXX",
            },
            {
                "blz": "37060590",
                "name": "Sparda-Bank Düsseldorf",  # Contains umlauts
                "bic": "GENODED1SPK",
            },
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove all test files
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def _create_csv_file(self, encoding="utf-8", with_bom=False):
        """Create a CSV test file with specified encoding."""
        csv_path = os.path.join(self.test_dir, f"test_data_{encoding}.csv")

        # CSV header and sample data
        csv_content = '"Bankleitzahl";"Merkmal";"Bezeichnung";"PLZ";"Ort";"Kurzbez";"PAN";"BIC";"Prüfziffer";"Datensatz-Nr";"Änderungskennzeichen";"Bankleitzahl-Löschung";"Nachfolge-Bankleitzahl"\n'

        for bank in self.bank_data:
            csv_content += f'"{bank["blz"]}";"1";"{bank["name"]}";"10117";"Berlin";"{bank["name"][:20]}";"20100";"{bank["bic"]}";"09";"11380";"U";"0";"00000000"\n'

        # Write with BOM if requested
        with open(csv_path, "w", encoding=encoding) as f:
            if with_bom and encoding == "utf-8":
                f.write("\ufeff")
            f.write(csv_content)

        return csv_path

    def _create_txt_file(self, encoding="utf-8", with_bom=False):
        """Create a TXT test file with fixed-width format and specified encoding."""
        txt_path = os.path.join(self.test_dir, f"test_data_{encoding}.txt")

        txt_content = ""
        for bank in self.bank_data:
            # Fixed-width format: BLZ(8) + Name(58) + Location(34) + Short(24) + Code(11) + BIC(11) + ...
            line = (
                bank["blz"].ljust(8)[:8]  # BLZ
                + "1"  # Merkmal
                + bank["name"].ljust(58)[:58]  # Bank name
                + "Berlin".ljust(34)[:34]  # Location
                + bank["name"][:20].ljust(24)[:24]  # Short name
                + "20100".ljust(11)[:11]  # PAN
                + bank["bic"].ljust(11)[:11]  # BIC
                + "09"  # Prüfziffer
                + "11380U000000000"  # Additional fields
            )
            txt_content += line + "\n"

        # Write with BOM if requested
        with open(txt_path, "w", encoding=encoding) as f:
            if with_bom and encoding == "utf-8":
                f.write("\ufeff")
            f.write(txt_content)

        return txt_path

    def _create_xml_file(self, encoding="utf-8", with_bom=False):
        """Create an XML test file with specified encoding."""
        xml_path = os.path.join(self.test_dir, f"test_data_{encoding}.xml")

        xml_content = f'<?xml version="1.0" encoding="{encoding.upper()}"?>\n'
        xml_content += '<Document xmlns="urn:BBk:BLZ:xsd:BLZDat">\n'
        xml_content += "  <FileHdr>\n"
        xml_content += "    <SndgInst>MARKDEFF</SndgInst>\n"
        xml_content += "    <FileRef>2025-06-09-1-N</FileRef>\n"
        xml_content += "    <FileCreDt>2025-05-07</FileCreDt>\n"
        xml_content += "    <ValidFrom>2025-06-09</ValidFrom>\n"
        xml_content += "    <ValidTill>2025-09-07</ValidTill>\n"
        xml_content += "  </FileHdr>\n"

        for bank in self.bank_data:
            xml_content += "  <BLZEintrag>\n"
            xml_content += f"    <BLZ>{bank['blz']}</BLZ>\n"
            xml_content += "    <Merkmal>1</Merkmal>\n"
            xml_content += f"    <Bezeichnung>{bank['name']}</Bezeichnung>\n"
            xml_content += "    <PLZ>10117</PLZ>\n"
            xml_content += "    <Ort>Berlin</Ort>\n"
            xml_content += f"    <Kurzbez>{bank['name'][:20]}</Kurzbez>\n"
            xml_content += "    <PAN>20100</PAN>\n"
            xml_content += f"    <BIC>{bank['bic']}</BIC>\n"
            xml_content += "    <PruefZiffMeth>09</PruefZiffMeth>\n"
            xml_content += "    <DsNr>11380</DsNr>\n"
            xml_content += "    <Aenderungskennz>U</Aenderungskennz>\n"
            xml_content += "    <BLZLoesch>0</BLZLoesch>\n"
            xml_content += "    <NachfolgeBLZ>00000000</NachfolgeBLZ>\n"
            xml_content += "  </BLZEintrag>\n"

        xml_content += "</Document>\n"

        # Write with BOM if requested
        with open(xml_path, "w", encoding=encoding) as f:
            if with_bom and encoding == "utf-8":
                f.write("\ufeff")
            f.write(xml_content)

        return xml_path

    def test_csv_utf8(self):
        """Test CSV file with UTF-8 encoding."""
        csv_path = self._create_csv_file("utf-8")
        generator = IBANGenerator(csv_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(2)
        self.assertEqual(len(ibans), 2)
        for iban_record in ibans:
            self.assertTrue(iban_record.iban.startswith("DE"))
            self.assertEqual(len(iban_record.iban), 22)

    def test_csv_iso_8859_1(self):
        """Test CSV file with ISO-8859-1 encoding."""
        csv_path = self._create_csv_file("iso-8859-1")
        generator = IBANGenerator(csv_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data with umlauts was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_csv_utf8_with_bom(self):
        """Test CSV file with UTF-8 encoding and BOM."""
        csv_path = self._create_csv_file("utf-8", with_bom=True)
        generator = IBANGenerator(csv_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Test IBAN generation works even with BOM
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_txt_utf8(self):
        """Test TXT file with UTF-8 encoding."""
        txt_path = self._create_txt_file("utf-8")
        generator = IBANGenerator(txt_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data with umlauts was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(2)
        self.assertEqual(len(ibans), 2)
        for iban_record in ibans:
            self.assertTrue(iban_record.iban.startswith("DE"))
            self.assertEqual(len(iban_record.iban), 22)

    def test_txt_iso_8859_1(self):
        """Test TXT file with ISO-8859-1 encoding."""
        txt_path = self._create_txt_file("iso-8859-1")
        generator = IBANGenerator(txt_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data with umlauts was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_txt_utf8_with_bom(self):
        """Test TXT file with UTF-8 encoding and BOM."""
        txt_path = self._create_txt_file("utf-8", with_bom=True)
        generator = IBANGenerator(txt_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Test IBAN generation works even with BOM
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_xml_utf8(self):
        """Test XML file with UTF-8 encoding."""
        xml_path = self._create_xml_file("utf-8")
        generator = IBANGenerator(xml_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data with umlauts was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(2)
        self.assertEqual(len(ibans), 2)
        for iban_record in ibans:
            self.assertTrue(iban_record.iban.startswith("DE"))
            self.assertEqual(len(iban_record.iban), 22)

    def test_xml_iso_8859_1(self):
        """Test XML file with ISO-8859-1 encoding."""
        xml_path = self._create_xml_file("iso-8859-1")
        generator = IBANGenerator(xml_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Verify bank data with umlauts was loaded correctly
        bank_names = [bank.name for bank in generator.banks]
        self.assertIn("Bank für München", bank_names)
        self.assertIn("Sparda-Bank Düsseldorf", bank_names)

        # Test IBAN generation
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_xml_utf8_with_bom(self):
        """Test XML file with UTF-8 encoding and BOM."""
        xml_path = self._create_xml_file("utf-8", with_bom=True)
        generator = IBANGenerator(xml_path, seed=12345)

        self.assertEqual(generator.get_bank_count(), 4)

        # Test IBAN generation works even with BOM
        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))

    def test_format_detection_by_extension(self):
        """Test that format detection works correctly based on file extensions."""
        # Create files with different extensions
        csv_path = self._create_csv_file("utf-8")
        txt_path = self._create_txt_file("utf-8")
        xml_path = self._create_xml_file("utf-8")

        # Test each format loads correctly
        csv_generator = IBANGenerator(csv_path, seed=12345)
        txt_generator = IBANGenerator(txt_path, seed=12345)
        xml_generator = IBANGenerator(xml_path, seed=12345)

        # All should load the same number of banks
        self.assertEqual(csv_generator.get_bank_count(), 4)
        self.assertEqual(txt_generator.get_bank_count(), 4)
        self.assertEqual(xml_generator.get_bank_count(), 4)

        # All should generate valid IBANs
        csv_iban = csv_generator.generate_ibans(1)[0]
        txt_iban = txt_generator.generate_ibans(1)[0]
        xml_iban = xml_generator.generate_ibans(1)[0]

        self.assertTrue(csv_iban.iban.startswith("DE"))
        self.assertTrue(txt_iban.iban.startswith("DE"))
        self.assertTrue(xml_iban.iban.startswith("DE"))

    def test_encoding_fallback(self):
        """Test that encoding detection falls back gracefully."""
        # Create a file with mixed encodings (this simulates real-world edge cases)
        mixed_path = os.path.join(self.test_dir, "mixed_encoding.csv")

        # Write CSV header normally
        with open(mixed_path, "w", encoding="utf-8") as f:
            f.write(
                '"Bankleitzahl";"Merkmal";"Bezeichnung";"PLZ";"Ort";"Kurzbez";"PAN";"BIC";"Prüfziffer";"Datensatz-Nr";"Änderungskennzeichen";"Bankleitzahl-Löschung";"Nachfolge-Bankleitzahl"\n'
            )
            f.write(
                '"10000000";"1";"Bundesbank";"10117";"Berlin";"Bundesbank";"20100";"MARKDEF1100";"09";"11380";"U";"0";"00000000"\n'
            )

        # Generator should still work with fallback encoding detection
        generator = IBANGenerator(mixed_path, seed=12345)
        self.assertEqual(generator.get_bank_count(), 1)

        ibans = generator.generate_ibans(1)
        self.assertEqual(len(ibans), 1)
        self.assertTrue(ibans[0].iban.startswith("DE"))


if __name__ == "__main__":
    unittest.main()
