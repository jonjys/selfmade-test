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
    skriv_avslut,
    skriv_leverans,
    skriv_ringlista,
    skriv_utkast,
    skriv_utkastfiler,
)
from a11yscan.scan import Sajtresultat, Sidresultat, Överträdelse


def normalisera(text: str) -> str:
    """Slår ihop all vitrymd till enkla mellanslag.

    Brödtexten är radbruten för att se bra ut i en e-postklient, vilket gör att
    en fras som "en tredjedel" kan delas av ett radslut. Ett test som letar
    efter fraser i prosa måste därför bortse från radbrytningar — annars
    testar det ombrytningen i stället för innehållet.
    """
    return " ".join(text.split())


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
    text = normalisera(utkast.brödtext)
    assert "nej tack" in text
    assert "en tredjedel" in text
    assert "Test Testsson" in text


def test_hela_sekvensen_skrivs(tmp_path: Path):
    """Fyra mejl per sajt: första, uppföljning, avslut och leverans."""
    filer = skriv_utkastfiler([_sajt(_brist("label"))], tmp_path, "Test Testsson")
    namn = sorted(f.name for f in filer)
    assert namn == ["1_forsta.eml", "2_uppfoljning.eml", "3_avslut.eml",
                    "4_leverans.eml"]
    # Alla ska ligga i en katalog per domän, så att en sajt går att jobba av.
    assert all(f.parent.name == "butiken_se" for f in filer)


def test_alla_utkast_har_tom_mottagare(tmp_path: Path):
    """Vi gissar aldrig en mottagaradress — den fylls i för hand."""
    filer = skriv_utkastfiler([_sajt(_brist("label"))], tmp_path, "Test Testsson")
    for fil in filer:
        innehåll = fil.read_text(encoding="utf-8")
        assert "To: \n" in innehåll or "To:\n" in innehåll, f"{fil.name} har mottagare"


def test_avslutet_saljer_inte():
    """Sista mejlet ska släppa taget, inte pressa på en gång till."""
    utkast = skriv_avslut(_sajt(_brist("label")), "Test Testsson")
    assert utkast is not None
    assert "slutar höra av mig" in normalisera(utkast.brödtext)
    assert "19 900" not in normalisera(utkast.brödtext)


def test_leveransmejlet_har_avgransningen():
    """Även när vi levererar gratis ska begränsningen stå med."""
    utkast = skriv_leverans(_sajt(_brist("label", "critical", 8)), "Test Testsson")
    assert utkast is not None
    text = normalisera(utkast.brödtext)
    assert "en tredjedel" in text
    assert "juridiskt utlåtande" in text
    assert "19 900 kr" in text


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


def test_oversatt_regel_utan_krok_ger_svensk_amnesrad():
    """En regel utan formulerad krok ska ändå ge svensk text, inte sitt id.

    Fallet kommer från naturkompaniet.se, vars värsta brist var
    aria-required-parent. Ämnesraden blev "naturkompaniet.se:
    aria-required-parent" innan regeln översattes.
    """
    utkast = skriv_utkast(_sajt(_brist("aria-required-parent", "critical", 24)), "T T")
    assert utkast is not None
    assert "aria-required-parent" not in utkast.ämne
    assert "förälder" in utkast.ämne


def test_helt_okand_regel_ger_neutral_amnesrad():
    """Även en regel vi aldrig sett ska ge en läsbar ämnesrad.

    axe lägger till regler mellan versioner. En ny sådan får aldrig hamna som
    rå-id i ämnesraden på ett säljmejl.
    """
    utkast = skriv_utkast(_sajt(_brist("nagon-helt-ny-axe-regel", "critical", 5)), "T T")
    assert utkast is not None
    assert "nagon-helt-ny-axe-regel" not in utkast.ämne
    assert "tillgängligheten brister" in utkast.ämne


def test_eml_filen_bevarar_texten_exakt(tmp_path: Path):
    """Texten ska överleva vägen genom .eml-filen utan att tappa ett tecken.

    Teckenkodning i mejl är en klassisk tyst felkälla: felet syns först i
    mottagarens klient, aldrig hos avsändaren. Testet läser filen binärt,
    vilket är det enda korrekta sättet för innehåll som inte är ren ASCII.
    """
    import email
    import email.policy

    sajt = _sajt(_brist("image-alt"), _brist("custom-no-visible-focus"))
    original = skriv_utkast(sajt, "Åsa Öberg-Ängström")
    assert original is not None

    filer = skriv_utkastfiler([sajt], tmp_path, "Åsa Öberg-Ängström")
    första = next(f for f in filer if f.name == "1_forsta.eml")

    with första.open("rb") as f:
        läst = email.message_from_binary_file(f, policy=email.policy.default)

    assert läst["Subject"] == original.ämne
    assert läst.get_content().rstrip("\n") == original.brödtext.rstrip("\n")
    # Svenska tecken och typografiska streck ska vara oskadda.
    for tecken in ("å", "ä", "ö", "Å", "Ö", "—"):
        assert tecken in läst.get_content()
