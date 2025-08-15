import os
import tempfile
import unittest
from click.testing import CliRunner

from gen_ibans.cli import main


CSV_HEADER = "Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfzifferberechnungsmethode;Datensatznummer;Änderungskennzeichen;Bankleitzahllöschung;Nachfolge-Bankleitzahl\n"
CSV_TWO_BANKS = (
    CSV_HEADER
    + '"10000000";"1";"Bundesbank";"10591";"Berlin";"BBk Berlin";"20100";"MARKDEF1100";"09";"011380";"U";"0";"00000000"\n'
    + '"37040044";"1";"Commerzbank";"50667";"Köln";"Commerzbank Köln";"24100";"COBADEFFXXX";"13";"024463";"U";"0";"00000000"\n'
)


class TestCLIFilters(unittest.TestCase):
    def setUp(self) -> None:
        # Write a temporary CSV with two banks
        self.temp_csv = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        )
        self.temp_csv.write(CSV_TWO_BANKS)
        self.temp_csv.close()

    def tearDown(self) -> None:
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)

    def _run(self, *args):
        runner = CliRunner()
        return runner.invoke(main, list(args))

    def test_filter_bank_name_case_insensitive(self):
        # Should match Bundesbank only, regardless of case
        result = self._run(
            self.temp_csv.name,
            "--count",
            "1",
            "--seed",
            "1",
            "--filter-bank-name",
            "bundesbank",
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("Loaded 1 banks", result.output)

    def test_filter_bic_case_insensitive(self):
        # Should match Commerzbank by BIC pattern
        result = self._run(
            self.temp_csv.name,
            "--count",
            "1",
            "--seed",
            "2",
            "--filter-bic",
            "cobadeff.*",
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("Loaded 1 banks", result.output)

    def test_filter_blz_regex_exact(self):
        # BLZ filter uses regex (no IGNORECASE), test exact match
        result = self._run(
            self.temp_csv.name,
            "--count",
            "1",
            "--seed",
            "3",
            "--filter-blz",
            "^37040044$",
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("Loaded 1 banks", result.output)

    def test_filter_invalid_regex_raises(self):
        result = self._run(
            self.temp_csv.name,
            "--count",
            "1",
            "--filter-bank-name",
            "(",  # invalid regex
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid filter regex", result.output)

    def test_filter_no_match_raises(self):
        result = self._run(
            self.temp_csv.name,
            "--count",
            "1",
            "--filter-bic",
            "NOMATCH",
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("No banks match the provided filter(s)", result.output)

    def test_filters_from_config_file(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Write CSV in CWD so we can reference by path
            csv_path = os.path.abspath("banks.csv")
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(CSV_TWO_BANKS)

            # Write config.toml in CWD with a filter for Bundesbank via [cli]
            config_toml = '[cli]\nfilter_bank_name = "Bundesbank"\n'
            with open("config.toml", "w", encoding="utf-8") as f:
                f.write(config_toml)

            # Invoke without filter flags; should pick up config
            result = runner.invoke(
                main,
                [csv_path, "--count", "1", "--seed", "7"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Loaded 1 banks", result.output)
