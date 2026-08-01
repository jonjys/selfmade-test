"""Tester för mejlutkasten.

Det viktigaste testet här är att en sajt utan resultat aldrig genererar ett
utkast. Ett mejl som påstår att vi hittat fel på en sajt vi inte kunde läsa
vore både pinsamt och skadligt.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from a11yscan.outreach import (
    första_meningen,
    skriv_ringlista,
    skriv_utkast,
    skriv_utkastfiler,
)
from a11yscan.scan import Sajtresultat, Sidresultat, Överträdelse


def _sajt(*överträdelser: Överträdelse, domän: str = "butiken.se") -> Sajtresultat:
    sida = Sidresultat(url=f"https://{domän}", sidtyp="Kassa")
    sida.överträdelser = list(överträdelser)
    return Sajtresultat(domän=domän, startadress=f"https://{domän}", sidor=[sida])


def _brist(regel_id: str, impact: str = "serious", antal: int = 2) -> Överträdelse:
    return Överträdelse(regel_id, impact, antal, "Kassa", "https://butiken.se", "")


def test_leder_med_konkret_brist_inte_hogst_graderad():
    """Tangentbordsfällan ska slå bildtexter, även när axe graderar dem lika.

    Ett mejl som säger 'kassan går inte att använda utan mus' öppnas. Ett som
    säger 'produktbilder saknar alternativtext' gör det inte lika ofta.
    """
    sajt = _sajt(
        _brist("image-alt", "critical", 40),
        _brist("custom-click-handler-not-focusable", "serious", 1),
    )
    utkast = skriv_utkast(sajt, "Test Testsson")
    assert utkast is not None
    assert "utan mus" in utkast.ämne
    assert utkast.ämne.startswith("butiken.se:")


def test_onabar_sajt_ger_inget_utkast():
    trasig = Sajtresultat(
        domän="nere.se",
        startadress="https://nere.se",
        sidor=[Sidresultat(url="https://nere.se", sidtyp="Startsida", fel="timeout")],
        fel="Startsidan kunde inte läsas in: timeout",
    )
    assert skriv_utkast(trasig, "Test Testsson") is None


def test_sajt_utan_brister_ger_inget_utkast():
    ren = _sajt(domän="perfekt.se")
    assert skriv_utkast(ren, "Test Testsson") is None


def test_utkast_innehaller_avanmalan_och_avgransning():
    utkast = skriv_utkast(_sajt(_brist("button-name")), "Test Testsson")
    assert utkast is not None
    assert "nej tack" in utkast.brödtext
    assert "en tredjedel" in utkast.brödtext
    assert "Test Testsson" in utkast.brödtext


def test_utkast_har_tom_mottagare(tmp_path: Path):
    """Vi gissar aldrig en mottagaradress — den fylls i för hand."""
    filer = skriv_utkastfiler([_sajt(_brist("label"))], tmp_path, "Test Testsson")
    assert len(filer) == 1
    innehåll = filer[0].read_text(encoding="utf-8")
    assert "To: \n" in innehåll or "To:\n" in innehåll


@pytest.mark.parametrize(
    "text, väntat",
    [
        # Förkortningar får inte kapa meningen — det gav tidigare punktlistor
        # som slutade med "En ikonknapp utan text — t."
        ("En ikonknapp utan text — t.ex. krysset — är osynlig för skärmläsare.",
         "En ikonknapp utan text — t.ex. krysset — är osynlig för skärmläsare"),
        ("Bl.a. kassan drabbas.", "Bl.a. kassan drabbas"),
        # Riktigt meningsslut ska däremot kapa.
        ("Texten går inte att läsa. Det gäller många.", "Texten går inte att läsa"),
        ("Utan avslutande punkt", "Utan avslutande punkt"),
    ],
)
def test_forsta_meningen_klarar_forkortningar(text: str, väntat: str):
    assert första_meningen(text) == väntat


def test_utkast_har_inga_stympade_punkter():
    utkast = skriv_utkast(_sajt(_brist("button-name"), _brist("image-alt")), "T T")
    assert utkast is not None
    for rad in utkast.brödtext.splitlines():
        if rad.startswith("- "):
            assert not rad.rstrip().endswith("t."), f"stympad rad: {rad}"
            assert len(rad) > 25, f"misstänkt kort rad: {rad}"


def test_ringlista_sorterar_varst_forst(tmp_path: Path):
    lindrig = _sajt(_brist("button-name", "serious", 1), domän="lindrig.se")
    varst = _sajt(_brist("label", "critical", 30), domän="varst.se")
    sökväg = skriv_ringlista([lindrig, varst], tmp_path / "ring.csv", "Test Testsson")
    rader = sökväg.read_text(encoding="utf-8").splitlines()
    assert rader[1].startswith("varst.se")
