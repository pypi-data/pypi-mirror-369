"""
Tests for the CLI interface module.

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
import csv
from unittest.mock import patch
from io import StringIO
from click.testing import CliRunner

from gen_ibans.cli import OutputFormatter, main
from gen_ibans.iban_generator import BankInfo, IBANRecord, PersonalInfo


class TestOutputFormatter(unittest.TestCase):
    """Test OutputFormatter class."""

    def setUp(self):
        """Set up test fixtures."""
        person1 = PersonalInfo("Max", "Mustermann", "Musterstraße 1", "Berlin", "10115")
        person2 = PersonalInfo("Anna", "Schmidt", "Hauptstraße 42", "München", "80331")

        self.test_ibans = [
            IBANRecord(
                "DE89370400440532013000",
                BankInfo("37040044", "COBADEFFXXX", "Commerzbank"),
                person1,
            ),
            IBANRecord(
                "DE02120300000000202051",
                BankInfo("12030000", "BYLADEM1XXX", "Deutsche Bank"),
                person2,
            ),
        ]

    @patch("sys.stdout", new_callable=StringIO)
    def test_format_stdout_with_all_info(self, mock_stdout):
        """Test stdout formatting with all information."""
        OutputFormatter.format_stdout(
            self.test_ibans, include_bank_info=True, include_personal_info=True
        )

        output = mock_stdout.getvalue()
        self.assertIn(
            "DE89370400440532013000 | Max Mustermann | Musterstraße 1, 10115 Berlin | Commerzbank | COBADEFFXXX | 37040044",
            output,
        )
        self.assertIn(
            "DE02120300000000202051 | Anna Schmidt | Hauptstraße 42, 80331 München | Deutsche Bank | BYLADEM1XXX | 12030000",
            output,
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_format_stdout_iban_only(self, mock_stdout):
        """Test stdout formatting with IBAN only."""
        OutputFormatter.format_stdout(
            self.test_ibans, include_bank_info=False, include_personal_info=False
        )

        output = mock_stdout.getvalue()
        lines = output.strip().split("\n")
        self.assertEqual(lines[0], "DE89370400440532013000")
        self.assertEqual(lines[1], "DE02120300000000202051")
        self.assertNotIn("Commerzbank", output)
        self.assertNotIn("Max Mustermann", output)

    @patch("sys.stdout", new_callable=StringIO)
    def test_format_stdout_bank_info_only(self, mock_stdout):
        """Test stdout formatting with bank information only."""
        OutputFormatter.format_stdout(
            self.test_ibans, include_bank_info=True, include_personal_info=False
        )

        output = mock_stdout.getvalue()
        self.assertIn(
            "DE89370400440532013000 | Commerzbank | COBADEFFXXX | 37040044", output
        )
        self.assertIn(
            "DE02120300000000202051 | Deutsche Bank | BYLADEM1XXX | 12030000", output
        )
        self.assertNotIn("Max Mustermann", output)
        self.assertNotIn("Anna Schmidt", output)

    def test_format_txt_with_bank_info(self):
        """Test text file formatting with bank information."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            temp_path = temp_file.name

        try:
            with patch("sys.stdout", new_callable=StringIO):
                OutputFormatter.format_txt(
                    self.test_ibans,
                    temp_path,
                    include_bank_info=True,
                    include_personal_info=True,
                )

            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn(
                "DE89370400440532013000 | Max Mustermann | Musterstraße 1, 10115 Berlin | Commerzbank | COBADEFFXXX | 37040044",
                content,
            )
            self.assertIn(
                "DE02120300000000202051 | Anna Schmidt | Hauptstraße 42, 80331 München | Deutsche Bank | BYLADEM1XXX | 12030000",
                content,
            )
        finally:
            os.unlink(temp_path)

    def test_format_txt_bank_info_only(self):
        """Test text file formatting with bank information only."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            temp_path = temp_file.name

        try:
            with patch("sys.stdout", new_callable=StringIO):
                OutputFormatter.format_txt(
                    self.test_ibans,
                    temp_path,
                    include_bank_info=True,
                    include_personal_info=False,
                )

            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn(
                "DE89370400440532013000 | Commerzbank | COBADEFFXXX | 37040044", content
            )
            self.assertIn(
                "DE02120300000000202051 | Deutsche Bank | BYLADEM1XXX | 12030000",
                content,
            )
            self.assertNotIn("Max Mustermann", content)
            self.assertNotIn("Anna Schmidt", content)
        finally:
            os.unlink(temp_path)

    def test_format_txt_iban_only(self):
        """Test text file formatting with IBAN only."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as temp_file:
            temp_path = temp_file.name

        try:
            with patch("sys.stdout", new_callable=StringIO):
                OutputFormatter.format_txt(
                    self.test_ibans,
                    temp_path,
                    include_bank_info=False,
                    include_personal_info=False,
                )

            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.strip().split("\n")
            self.assertEqual(lines[0], "DE89370400440532013000")
            self.assertEqual(lines[1], "DE02120300000000202051")
            self.assertNotIn("Commerzbank", content)
        finally:
            os.unlink(temp_path)

    def test_format_csv(self):
        """Test CSV file formatting."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        ) as temp_file:
            temp_path = temp_file.name

        try:
            with patch("sys.stdout", new_callable=StringIO):
                OutputFormatter.format_csv(self.test_ibans, temp_path)

            with open(temp_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            # Check header
            self.assertEqual(
                rows[0],
                [
                    "IBAN",
                    "First Name",
                    "Last Name",
                    "Street Address",
                    "City",
                    "Postal Code",
                    "Bank Name",
                    "BIC",
                    "Bank Code",
                ],
            )

            # Check data
            self.assertEqual(
                rows[1],
                [
                    "DE89370400440532013000",
                    "Max",
                    "Mustermann",
                    "Musterstraße 1",
                    "Berlin",
                    "10115",
                    "Commerzbank",
                    "COBADEFFXXX",
                    "37040044",
                ],
            )
            self.assertEqual(
                rows[2],
                [
                    "DE02120300000000202051",
                    "Anna",
                    "Schmidt",
                    "Hauptstraße 42",
                    "München",
                    "80331",
                    "Deutsche Bank",
                    "BYLADEM1XXX",
                    "12030000",
                ],
            )
        finally:
            os.unlink(temp_path)

    @patch("sys.stderr", new_callable=StringIO)
    def test_format_txt_file_error(self, mock_stderr):
        """Test text file formatting error handling."""
        invalid_path = "/invalid/path/file.txt"

        with self.assertRaises(SystemExit):
            OutputFormatter.format_txt(self.test_ibans, invalid_path)

        self.assertIn("Error writing to file", mock_stderr.getvalue())

    @patch("sys.stderr", new_callable=StringIO)
    def test_format_csv_file_error(self, mock_stderr):
        """Test CSV file formatting error handling."""
        invalid_path = "/invalid/path/file.csv"

        with self.assertRaises(SystemExit):
            OutputFormatter.format_csv(self.test_ibans, invalid_path)

        self.assertIn("Error writing to CSV file", mock_stderr.getvalue())


# Obsolete test classes removed - these functions don't exist in current CLI implementation


class TestMainFunction(unittest.TestCase):
    """Test main CLI function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a sample CSV content
        self.csv_content = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfzifferberechnungsmethode;Datensatznummer;Änderungskennzeichen;Bankleitzahllöschung;Nachfolge-Bankleitzahl
"10000000";"1";"Bundesbank";"10591";"Berlin";"BBk Berlin";"20100";"MARKDEF1100";"09";"011380";"U";"0";"00000000"
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

    def test_main_stdout_output(self):
        """Test main function with stdout output."""
        runner = CliRunner()
        result = runner.invoke(
            main, [self.temp_csv.name, "--count", "2", "--seed", "42"]
        )

        self.assertEqual(result.exit_code, 0)

        # Check that IBANs were generated and printed
        lines = [line for line in result.output.split("\n") if line.startswith("DE")]
        self.assertEqual(len(lines), 2)

        # Check stderr messages (Click captures both stdout and stderr in output)
        self.assertIn("Loading bank data", result.output)
        self.assertIn("Loaded 2 banks", result.output)
        self.assertIn("Successfully generated 2 IBANs", result.output)

    def test_main_txt_output(self):
        """Test main function with txt file output."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as output_file:
            output_path = output_file.name

        try:
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    self.temp_csv.name,
                    "--count",
                    "3",
                    "--seed",
                    "123",
                    "--format",
                    "txt",
                    "--output",
                    output_path,
                ],
            )

            self.assertEqual(result.exit_code, 0)

            # Check that file was created and contains IBANs
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = [line for line in content.split("\n") if line.startswith("DE")]
            self.assertEqual(len(lines), 3)

            self.assertIn("Successfully generated 3 IBANs", result.output)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_main_csv_output(self):
        """Test main function with CSV file output."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        ) as output_file:
            output_path = output_file.name

        try:
            runner = CliRunner()
            result = runner.invoke(
                main,
                [
                    self.temp_csv.name,
                    "--count",
                    "2",
                    "--seed",
                    "456",
                    "--format",
                    "csv",
                    "--output",
                    output_path,
                ],
            )

            self.assertEqual(result.exit_code, 0)

            # Check that CSV file was created with proper structure
            with open(output_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)

            self.assertEqual(len(rows), 3)  # Header + 2 data rows
            self.assertEqual(
                rows[0],
                [
                    "IBAN",
                    "First Name",
                    "Last Name",
                    "Street Address",
                    "City",
                    "Postal Code",
                    "Bank Name",
                    "BIC",
                    "Bank Code",
                ],
            )

            # Check that data rows contain valid IBANs
            for i in range(1, 3):
                self.assertTrue(rows[i][0].startswith("DE"))
                self.assertEqual(len(rows[i][0]), 22)

            self.assertIn("Successfully generated 2 IBANs", result.output)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_main_file_not_found_error(self):
        """Test main function error handling for missing file."""
        runner = CliRunner()
        result = runner.invoke(main, ["nonexistent.csv"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Error:", result.output)

    def test_main_generation_error(self):
        """Test main function error handling during generation."""
        # Create CSV with no valid banks
        csv_content_no_bic = """Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfzifferberechnungsmethode;Datensatznummer;Änderungskennzeichen;Bankleitzahllöschung;Nachfolge-Bankleitzahl
"10000000";"1";"Bundesbank";"10591";"Berlin";"BBk Berlin";"20100";"";"09";"011380";"U";"0";"00000000"
"""

        temp_csv_no_bic = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        )
        temp_csv_no_bic.write(csv_content_no_bic)
        temp_csv_no_bic.close()

        try:
            runner = CliRunner()
            result = runner.invoke(main, [temp_csv_no_bic.name, "--count", "1"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error:", result.output)
        finally:
            os.unlink(temp_csv_no_bic.name)


if __name__ == "__main__":
    unittest.main()
