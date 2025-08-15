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

import os
import tempfile

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


def test_beneficiaries_can_be_legal_entities_when_configured():
    """If beneficiary_legal_entity_probability=1.0, all beneficiaries must be LegalEntity.

    Only valid when account holders are natural persons (i.e., legal_entity_probability=0.0),
    otherwise beneficiaries are blocked by business rule.
    """
    path = _csv_one_bank()
    try:
        cfg = GeneratorConfig(
            legal_entity_probability=0.0,  # ensure holders are natural persons
            beneficiary_legal_entity_probability=1.0,  # force legal entity beneficiaries
            account_holder_distribution=[(1, 1.0)],  # one holder
            beneficial_owner_distribution=[
                (3, 1.0)
            ],  # up to 3 beneficiaries per account
        )
        gen = IBANGenerator(path, seed=101, config=cfg)
        recs = gen.generate_ibans(8)

        for rec in recs:
            # Holders are all natural persons
            assert all(isinstance(h, PersonalInfo) for h in rec.account_holders)
            # Beneficiaries present are LegalEntity (count can be 0..3)
            assert all(isinstance(b, LegalEntity) for b in rec.beneficiaries)
            assert len(rec.beneficiaries) <= 3
            # LegalEntity WID format: 'DE' + 9 digits, optionally '-' + 5-digit feature
            for b in rec.beneficiaries:
                wid = b.wid
                base, sep, feature = wid.partition("-")
                assert wid.startswith("DE") and (
                    (sep == "" and len(wid) == 11 and wid[2:].isdigit())
                    or (
                        sep == "-"
                        and len(base) == 11
                        and base[2:].isdigit()
                        and len(feature) == 5
                        and feature.isdigit()
                    )
                )
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_max_limits_respected_for_holders_and_beneficiaries():
    """Generated counts must not exceed configured maxima from distributions."""
    path = _csv_one_bank()
    try:
        cfg = GeneratorConfig(
            legal_entity_probability=0.0,  # natural person holders only
            account_holder_distribution=[(4, 1.0)],  # up to 4 holders
            beneficial_owner_distribution=[(5, 1.0)],  # up to 5 beneficiaries
        )
        gen = IBANGenerator(path, seed=202, config=cfg)
        recs = gen.generate_ibans(20)

        for rec in recs:
            assert 1 <= len(rec.account_holders) <= 4
            assert 0 <= len(rec.beneficiaries) <= 5
            # All holders and beneficiaries are natural persons under this config
            assert all(isinstance(h, PersonalInfo) for h in rec.account_holders)
            assert all(isinstance(b, PersonalInfo) for b in rec.beneficiaries)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_tax_id_format_for_all_persons():
    """All PersonalInfo objects generated must have a valid 11-digit numeric Tax-ID."""
    path = _csv_one_bank()
    try:
        cfg = GeneratorConfig(
            legal_entity_probability=0.0,
            account_holder_distribution=[(3, 1.0)],  # 1..3 holders
            beneficial_owner_distribution=[(3, 1.0)],  # 0..3 beneficiaries
            economically_active_probability=0.5,  # mix of active/non-active
        )
        gen = IBANGenerator(path, seed=303, config=cfg)
        recs = gen.generate_ibans(12)

        for rec in recs:
            for h in rec.account_holders:
                assert isinstance(h, PersonalInfo)
                assert h.tax_id is not None
                assert len(h.tax_id) == 11 and h.tax_id.isdigit()
            for b in rec.beneficiaries:
                assert isinstance(b, PersonalInfo)
                assert b.tax_id is not None
                assert len(b.tax_id) == 11 and b.tax_id.isdigit()
    finally:
        if os.path.exists(path):
            os.unlink(path)
