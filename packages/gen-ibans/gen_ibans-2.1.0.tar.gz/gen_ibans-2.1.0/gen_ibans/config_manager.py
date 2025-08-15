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

# Configuration management utilities for gen-ibans.
from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any
import json

from platformdirs import PlatformDirs

# Prefer confz for configuration handling; fall back gracefully if missing.
try:
    from confz import ConfZ, ConfZFileSource
    from pydantic import BaseModel, Field

    _CONFZ_AVAILABLE = True
except Exception:  # pragma: no cover
    _CONFZ_AVAILABLE = False
    BaseModel = object  # type: ignore

    def Field(*args, **kwargs):  # type: ignore
        return None


# Allowed configuration keys that map to GeneratorConfig fields
_ALLOWED_KEYS = {
    "account_holder_distribution",
    "beneficial_owner_distribution",
    "legal_entity_probability",
    "beneficiary_legal_entity_probability",
    "economically_active_probability",
    "wid_feature_distribution",
    "person_reuse_distribution",
}


class GeneratorSectionModel(BaseModel):  # type: ignore[misc]
    account_holder_distribution: Any = Field(
        default_factory=lambda: [
            [1, 0.70],
            [2, 0.15],
            [10, 0.14],
            [100, 0.009],
            [1000, 0.001],
        ]
    )
    beneficial_owner_distribution: Any = Field(
        default_factory=lambda: [
            [0, 0.70],
            [1, 0.20],
            [2, 0.05],
            [10, 0.04],
            [50, 0.009],
            [1000, 0.001],
        ]
    )
    legal_entity_probability: float = 0.05
    beneficiary_legal_entity_probability: float = 0.0
    economically_active_probability: float = 0.20
    wid_feature_distribution: Any = Field(
        default_factory=lambda: [
            [1, 0.80],
            [10, 0.15],
            [100, 0.04],
            [99999, 0.01],
        ]
    )
    person_reuse_distribution: Any = Field(
        default_factory=lambda: [
            [1, 0.8],
            [2, 0.1],
            [5, 0.05],
            [15, 0.03],
            [50, 0.019],
            [200, 0.001],
        ]
    )


class CLISectionModel(BaseModel):  # type: ignore[misc]
    # General CLI defaults
    count: int = 1
    seed: Optional[int] = None
    output_format: Optional[str] = None  # txt, csv, xml, json
    output: Optional[str] = None  # file path
    no_echo: bool = False
    iban_only: bool = False
    no_personal_info: bool = False
    no_bank_info: bool = False
    clean: bool = False
    no_color: bool = False
    # Optional regex filters
    filter_bank_name: Optional[str] = None
    filter_bic: Optional[str] = None
    filter_blz: Optional[str] = None


class DownloaderSectionModel(BaseModel):  # type: ignore[misc]
    download_format: str = "csv"  # csv, txt, xml
    force_download: bool = False
    cache_dir: Optional[str] = None
    no_version_check: bool = False


class AppConfigModel(BaseModel):  # type: ignore[misc]
    generator: GeneratorSectionModel = Field(default_factory=GeneratorSectionModel)
    cli: CLISectionModel = Field(default_factory=CLISectionModel)
    downloader: DownloaderSectionModel = Field(default_factory=DownloaderSectionModel)
    _descriptions: Dict[str, Any] = Field(default_factory=dict)


def get_default_config_path() -> Path:
    r"""Return the default path for the configuration file using platformdirs.

    On each OS this resolves to the user configuration directory, e.g.:
    - Windows: %APPDATA%\gen-ibans\config.toml
    - Linux: ~/.config/gen-ibans/config.toml
    - macOS: ~/Library/Application Support/gen-ibans/config.toml
    """
    dirs = PlatformDirs(appname="gen-ibans", appauthor=False)
    # appauthor False makes paths like ~/.config/gen-ibans on Linux
    config_dir = Path(dirs.user_config_dir)
    return config_dir / "config.toml"


def get_config_search_paths() -> list[Path]:
    """Return directories that are searched for a configuration file.

    Order of precedence:
    1. Current working directory
    2. Default per-OS configuration directory (PlatformDirs)
    """
    paths: list[Path] = [Path.cwd(), get_default_config_path().parent]
    return paths


def load_config_from_file(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load generator configuration values using ConfZ (if available) from TOML/JSON file(s).

    Behavior:
    - If config_path is provided, only that file is used.
    - Otherwise, search in get_config_search_paths() for a file named "config.toml"
      first, then "config.json" in each directory (current dir first), and use all
      existing ones in precedence order for ConfZ.

    Returns a dict with keys matching GeneratorConfig fields. Unknown keys are ignored.
    If no file exists, or values are invalid, returns an empty dict.
    """
    try:
        if config_path is not None:
            candidates = [Path(config_path)]
        else:
            candidates = []
            for base in get_config_search_paths():
                candidates.append(base / "config.toml")
            for base in get_config_search_paths():
                candidates.append(base / "config.json")
        existing = [p for p in candidates if p.exists()]
        if not existing:
            return {}

        if _CONFZ_AVAILABLE:

            class Config(ConfZ):  # type: ignore[misc]
                generator: GeneratorSectionModel
                _descriptions: Dict[str, Any] = {}
                CONFIG_SOURCES = tuple(ConfZFileSource(file=str(p)) for p in existing)

            cfg = Config()  # type: ignore[call-arg]
            gen = cfg.generator
            gen_dict = gen.__dict__ if hasattr(gen, "__dict__") else dict(gen)
        else:
            # Fallback: load the first existing file manually (TOML preferred)
            path = existing[0]
            # Try to parse TOML or JSON based on extension
            if path.suffix.lower() == ".toml":
                try:
                    import tomllib  # Python >=3.11

                    with open(path, "rb") as f:
                        data = tomllib.load(f)
                except Exception:
                    # Fallback to 'toml' package if available
                    try:
                        import toml  # type: ignore

                        with open(path, "r", encoding="utf-8") as f:
                            data = toml.load(f)
                    except Exception:
                        return {}
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            if not isinstance(data, dict):
                return {}
            # Expect structure with a [generator] table/object
            gen_dict = data.get("generator", {}) if isinstance(data, dict) else {}
            if not isinstance(gen_dict, dict):
                return {}
        return {k: v for k, v in gen_dict.items() if k in _ALLOWED_KEYS}
    except Exception:
        # Fail safe: ignore broken configs
        return {}


def load_full_config(config_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Load full configuration (generator, cli, downloader) from TOML/JSON.

    Returns a dict with keys: "generator", "cli", "downloader". Missing sections
    default to their model defaults. Unknown keys are ignored.
    """
    # Build candidate files as in load_config_from_file
    if config_path is not None:
        candidates = [Path(config_path)]
    else:
        candidates = []
        for base in get_config_search_paths():
            candidates.append(base / "config.toml")
        for base in get_config_search_paths():
            candidates.append(base / "config.json")
    existing = [p for p in candidates if p.exists()]
    if not existing:
        # Return defaults
        return {
            "generator": GeneratorSectionModel().__dict__
            if hasattr(GeneratorSectionModel(), "__dict__")
            else dict(GeneratorSectionModel()),
            "cli": CLISectionModel().__dict__
            if hasattr(CLISectionModel(), "__dict__")
            else dict(CLISectionModel()),
            "downloader": DownloaderSectionModel().__dict__
            if hasattr(DownloaderSectionModel(), "__dict__")
            else dict(DownloaderSectionModel()),
        }

    try:
        if _CONFZ_AVAILABLE:

            class FullConfig(ConfZ):  # type: ignore[misc]
                generator: GeneratorSectionModel
                cli: CLISectionModel = Field(default_factory=CLISectionModel)
                downloader: DownloaderSectionModel = Field(
                    default_factory=DownloaderSectionModel
                )
                _descriptions: Dict[str, Any] = {}
                CONFIG_SOURCES = tuple(ConfZFileSource(file=str(p)) for p in existing)

            cfg = FullConfig()  # type: ignore[call-arg]
            gen = cfg.generator
            cli = cfg.cli if hasattr(cfg, "cli") else CLISectionModel()  # type: ignore
            dl = (
                cfg.downloader
                if hasattr(cfg, "downloader")
                else DownloaderSectionModel()
            )  # type: ignore
            gen_dict = gen.__dict__ if hasattr(gen, "__dict__") else dict(gen)
            cli_dict = cli.__dict__ if hasattr(cli, "__dict__") else dict(cli)
            dl_dict = dl.__dict__ if hasattr(dl, "__dict__") else dict(dl)
            return {"generator": gen_dict, "cli": cli_dict, "downloader": dl_dict}
        else:
            # Fallback: load first existing file (prefer TOML) and read sections
            path = existing[0]
            if path.suffix.lower() == ".toml":
                try:
                    import tomllib

                    with open(path, "rb") as f:
                        data = tomllib.load(f)
                except Exception:
                    try:
                        import toml  # type: ignore

                        with open(path, "r", encoding="utf-8") as f:
                            data = toml.load(f)
                    except Exception:
                        data = {}
            else:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            data = data if isinstance(data, dict) else {}
            gen_dict = (
                data.get("generator", {})
                if isinstance(data.get("generator", {}), dict)
                else {}
            )
            cli_dict = (
                data.get("cli", {}) if isinstance(data.get("cli", {}), dict) else {}
            )
            dl_dict = (
                data.get("downloader", {})
                if isinstance(data.get("downloader", {}), dict)
                else {}
            )
            # Filter generator keys
            gen_dict = {k: v for k, v in gen_dict.items() if k in _ALLOWED_KEYS}
            return {"generator": gen_dict, "cli": cli_dict, "downloader": dl_dict}
    except Exception:
        return {"generator": {}, "cli": {}, "downloader": {}}


def default_config_toml() -> str:
    """Return the default configuration as a commented TOML string.

    Includes documentation and example variants for all parameters.
    """
    return (
        "# gen-ibans Konfigurationsdatei (TOML)\n"
        "#\n"
        "# Diese Datei definiert Standardwerte für die CLI.\n"
        "# CLI-Parameter überschreiben Werte aus dieser Datei.\n"
        "#\n"
        "# Hinweise:\n"
        "# - Wahrscheinlichkeiten sind im Bereich 0.0 .. 1.0.\n"
        "# - Verteilungen sind Listen von [max_wert, wahrscheinlichkeit] Paaren.\n"
        "# - Die Summe der Wahrscheinlichkeiten in einer Verteilung sollte 1.0 ergeben.\n"
        "#\n\n"
        "[generator]\n"
        "# Wahrscheinlichkeit, dass der Kontoinhaber eine juristische Person ist (0..1).\n"
        "legal_entity_probability = 0.05\n\n"
        "# Wahrscheinlichkeit, dass natürliche Personen wirtschaftlich tätig sind (0..1).\n"
        "economically_active_probability = 0.20\n\n"
        "# Wahrscheinlichkeit, dass wirtschaftlich Berechtigte juristische Personen sind (derzeit 0).\n"
        "beneficiary_legal_entity_probability = 0.0\n\n"
        "# Verteilung der Anzahl der Kontoinhaber als Liste von [max_anzahl, wahrscheinlichkeit].\n"
        "# Beispiel (Default): ein Inhaber 70%, zwei Inhaber 15%, bis 10: 14%, bis 100: 0.9%, bis 1000: 0.1%\n"
        "account_holder_distribution = [[1, 0.70], [2, 0.15], [10, 0.14], [100, 0.009], [1000, 0.001]]\n"
        "# Variante (kommentiert): höhere Mehrpersonenkonten\n"
        "# account_holder_distribution = [[1, 0.60], [2, 0.25], [10, 0.13], [100, 0.019], [1000, 0.001]]\n\n"
        "# Verteilung der Anzahl wirtschaftlich Berechtigter als Liste von [max_anzahl, wahrscheinlichkeit].\n"
        "beneficial_owner_distribution = [[0, 0.70], [1, 0.20], [2, 0.05], [10, 0.04], [50, 0.009], [1000, 0.001]]\n"
        "# Variante: häufiger 1 wirtschaftlich Berechtigter\n"
        "# beneficial_owner_distribution = [[0, 0.50], [1, 0.35], [2, 0.10], [10, 0.04], [50, 0.009], [1000, 0.001]]\n\n"
        "# WID Unterscheidungsmerkmal (nur natürliche Personen) als [max_wert, wahrscheinlichkeit].\n"
        "# 1 -> 00001, 10 -> 00002-00010, 100 -> 00011-00100, 99999 -> 00101-99999\n"
        "wid_feature_distribution = [[1, 0.80], [10, 0.15], [100, 0.04], [99999, 0.01]]\n"
        "# Variante: mehr hohe Merkmale\n"
        "# wid_feature_distribution = [[1, 0.60], [10, 0.20], [100, 0.15], [99999, 0.05]]\n\n"
        "# Wiederverwendung von Personen (wie oft dieselbe Person vorkommt) als [max_anzahl, wahrscheinlichkeit].\n"
        "person_reuse_distribution = [[1, 0.8], [2, 0.1], [5, 0.05], [15, 0.03], [50, 0.019], [200, 0.001]]\n"
        "# Variante: mehr Wiederverwendung im Long Tail\n"
        "# person_reuse_distribution = [[1, 0.7], [2, 0.15], [5, 0.07], [15, 0.05], [50, 0.028], [200, 0.002]]\n"
        "\n"
        "[downloader]\n"
        "# Standardformat beim automatischen Download von der Bundesbank (csv|txt|xml).\n"
        'download_format = "csv"\n'
        "# Erzwinge Neu-Download auch wenn Cache vorhanden ist.\n"
        "force_download = false\n"
        "# Optionaler Cache-Ordner (Pfad als String).\n"
        '# cache_dir = ".\\cache"\n'
        "# Online-Versionsprüfung deaktivieren (nur Cache-Alter nutzen).\n"
        "no_version_check = false\n"
        "\n"
        "[cli]\n"
        "# Standardanzahl zu generierender IBANs, wenn nicht per CLI angegeben.\n"
        "count = 1\n"
        "# Fester Seed für deterministische Ergebnisse (optional).\n"
        "# seed = 12345\n"
        "# Ausgabeformat (txt|csv|xml|json); leer bedeutet Plain-Text.\n"
        '# output_format = "json"\n'
        "# Ausgabedatei-Pfad; leer bedeutet stdout.\n"
        '# output = ".\\ibans.json"\n'
        "# Unterdrücke stdout, wenn in Datei geschrieben wird.\n"
        "no_echo = false\n"
        "# Nur IBANs ohne Bank- und Personendaten ausgeben.\n"
        "iban_only = false\n"
        "# Personenbezogene Daten ausblenden.\n"
        "no_personal_info = false\n"
        "# Bankinformationen ausblenden.\n"
        "no_bank_info = false\n"
        "# Zusätzliche Informationsmeldungen unterdrücken.\n"
        "clean = false\n"
        "# Farbige Ausgabe deaktivieren.\n"
        "no_color = false\n"
        "#\n"
        "# Regex-Filter für Bankenliste (optional). CLI-Flags überschreiben diese Werte.\n"
        "# Beachte: filter_bank_name und filter_bic sind case-insensitive; filter_blz ist exakt.\n"
        "# Beispiele:\n"
        '# filter_bank_name = "(Sparkasse|Volksbank)"\n'
        '# filter_bic = "DEUTDEFF.*"\n'
        '# filter_blz = "^10020030$"\n'
        "#\n"
        "# Standardmäßig sind keine Filter gesetzt (alle Banken).\n"
        '# filter_bank_name = ""\n'
        '# filter_bic = ""\n'
        '# filter_blz = ""\n'
    )


def write_default_config_file(target: Optional[Path] = None) -> Path:
    """Write the default configuration file (TOML) to the target (or default path) and return the path."""
    path = target or get_default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Ensure .toml extension if target is a directory path or wrong extension
    if path.suffix.lower() != ".toml":
        # If a directory was passed accidentally, append config.toml
        if path.exists() and path.is_dir():
            path = path / "config.toml"
        else:
            # Replace extension with .toml
            path = path.with_suffix(".toml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(default_config_toml())
    return path
