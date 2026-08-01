"""Tester för inläsning av adresslistan."""

from __future__ import annotations

from pathlib import Path

from a11yscan.cli import _läs_sajter


def test_dubbletter_tas_bort(tmp_path: Path):
    """En dubblett skriver annars över sin egen rapport utan att något syns."""
    fil = tmp_path / "sajter.txt"
    fil.write_text(
        "butiken.se\n"
        "annan.se\n"
        "https://butiken.se\n"
        "BUTIKEN.se/\n",
        encoding="utf-8",
    )
    assert _läs_sajter(fil) == ["https://butiken.se", "https://annan.se"]


def test_kommentarer_och_tomrader_hoppas_over(tmp_path: Path):
    fil = tmp_path / "sajter.txt"
    fil.write_text("# rubrik\n\n  butiken.se  \n\n# slut\n", encoding="utf-8")
    assert _läs_sajter(fil) == ["https://butiken.se"]


def test_ordningen_bevaras(tmp_path: Path):
    """Listan ska gå att jobba av uppifrån i den ordning den skrevs."""
    fil = tmp_path / "sajter.txt"
    fil.write_text("c.se\na.se\nb.se\n", encoding="utf-8")
    assert _läs_sajter(fil) == ["https://c.se", "https://a.se", "https://b.se"]
