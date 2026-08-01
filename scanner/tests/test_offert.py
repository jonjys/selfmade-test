"""Tester för offerten.

Offerten är ett dokument som går till en betalande kund. Det som testas här är
inte layouten utan de påståenden som inte får glida — priset, giltighetstiden
och att vi aldrig lovar godkännande.
"""

from __future__ import annotations

from datetime import date, timedelta

from a11yscan.offert import (
    GILTIGHET_DAGAR,
    PRIS_GRANSKNING,
    TUSENTAL,
    kr,
    offert_html,
)
from a11yscan.scan import Sajtresultat, Sidresultat, Överträdelse


def _sajt(brott: int = 12, domän: str = "butiken.se") -> Sajtresultat:
    sida = Sidresultat(url=f"https://{domän}", sidtyp="Kassa")
    sida.överträdelser = [
        Överträdelse("label", "critical", brott, "Kassa", f"https://{domän}", "")
    ]
    return Sajtresultat(domän=domän, startadress=f"https://{domän}", sidor=[sida])


def test_belopp_formateras_med_hart_mellanslag():
    """Svenska använder mellanslag, inte komma — och hårt så beloppet håller ihop."""
    assert kr(19_900) == f"19{TUSENTAL}900"
    assert kr(1_150) == f"1{TUSENTAL}150"
    assert kr(900) == "900"
    assert "," not in kr(19_900)


def test_offerten_visar_pris_och_giltighet():
    html = offert_html(_sajt(), mottagare="Butiken AB", avsändare="Test Testsson")
    assert kr(PRIS_GRANSKNING) in html
    assert "19,900" not in html, "komma som avgränsare har läckt in"
    giltig = date.today() + timedelta(days=GILTIGHET_DAGAR)
    assert giltig.isoformat() in html


def test_offerten_lovar_aldrig_godkannande():
    html = offert_html(_sajt(), mottagare="Butiken AB", avsändare="Test Testsson")
    assert "ingen garanti" in html
    assert "Ingen leverantör kan lova det" in html


def test_offerten_anvander_skanningens_siffror():
    html = offert_html(_sajt(brott=37), mottagare="X", avsändare="Y")
    assert "37 element" in html


def test_offert_utan_genomford_skanning_faller_tillbaka():
    """Utan siffror ska offerten inte hitta på några."""
    trasig = Sajtresultat(domän="nere.se", startadress="https://nere.se",
                          fel="kunde inte läsas in")
    html = offert_html(trasig, mottagare="X", avsändare="Y")
    assert "normalstort e-handelsflöde" in html
    assert "element</b> som bryter" not in html
