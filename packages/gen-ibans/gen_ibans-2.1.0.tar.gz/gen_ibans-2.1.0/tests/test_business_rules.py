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

from gen_ibans.iban_generator import (
    IBANGenerator,
    GeneratorConfig,
    PersonalInfo,
    LegalEntity,
)


def _csv_one_bank() -> str:
    content = (
        "Bankleitzahl;Merkmal;Bezeichnung;PLZ;Ort;Kurzbezeichnung;PAN;BIC;Prüfziffer-berechnungsverfahren;Datensatz-Nummer;Änderungskennzeichen;Löschung;Nachfolge-Bankleitzahl\n"
        "10010010;1;Postbank;10115;Berlin;Postbank;52011;PBNKDEFF;;1;;;;;\n"
    )
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    f.write(content)
    f.close()
    return f.name


def test_legal_entity_has_no_beneficiaries():
    path = _csv_one_bank()
    try:
        cfg = GeneratorConfig(
            legal_entity_probability=1.0,
            beneficial_owner_distribution=[
                (10, 1.0)
            ],  # even if requested, legal entities must block beneficiaries
        )
        gen = IBANGenerator(path, seed=7, config=cfg)
        records = gen.generate_ibans(5)
        # All account holders should be LegalEntity and beneficiaries empty
        for rec in records:
            assert all(isinstance(h, LegalEntity) for h in rec.account_holders)
            assert rec.beneficiaries == []
    finally:
        if os.path.exists(path):
            os.unlink(path)


essential_counts = 8


def test_wid_present_only_when_economically_active():
    path = _csv_one_bank()
    try:
        # No one economically active
        cfg_inactive = GeneratorConfig(
            legal_entity_probability=0.0,
            economically_active_probability=0.0,
            account_holder_distribution=[(1, 1.0)],
            beneficial_owner_distribution=[(1, 1.0)],
        )
        gen_inactive = IBANGenerator(path, seed=42, config=cfg_inactive)
        recs_inactive = gen_inactive.generate_ibans(essential_counts)
        for rec in recs_inactive:
            for h in rec.account_holders:
                assert isinstance(h, PersonalInfo)
                assert h.wid is None
            for b in rec.beneficiaries:
                assert isinstance(b, PersonalInfo)
                assert b.wid is None

        # Everyone economically active
        cfg_active = GeneratorConfig(
            legal_entity_probability=0.0,
            economically_active_probability=1.0,
            account_holder_distribution=[(1, 1.0)],
            beneficial_owner_distribution=[(1, 1.0)],
        )
        gen_active = IBANGenerator(path, seed=43, config=cfg_active)
        recs_active = gen_active.generate_ibans(essential_counts)
        for rec in recs_active:
            for h in rec.account_holders:
                assert isinstance(h, PersonalInfo)
                assert h.wid is not None and h.wid.startswith("DE") and len(h.wid) == 13
            for b in rec.beneficiaries:
                assert isinstance(b, PersonalInfo)
                assert b.wid is not None and b.wid.startswith("DE") and len(b.wid) == 13
    finally:
        if os.path.exists(path):
            os.unlink(path)
