"""Tester för tillgänglighetsredogörelsen.

Dokumentet publiceras på kundens egen sajt och läses potentiellt av en
tillsynsmyndighet. Det som testas här är de påståenden som inte får glida.
"""

from __future__ import annotations

from a11yscan.redogorelse import redogörelse_markdown
from a11yscan.scan import Sajtresultat, Sidresultat, Överträdelse


def _sajt(*brister: Överträdelse, domän: str = "butiken.se") -> Sajtresultat:
    sida = Sidresultat(url=f"https://{domän}", sidtyp="Startsida")
    sida.överträdelser = list(brister)
    return Sajtresultat(domän=domän, startadress=f"https://{domän}", sidor=[sida])


def _brist(regel_id: str, antal: int = 5, impact: str = "serious") -> Överträdelse:
    return Överträdelse(regel_id, impact, antal, "Startsida", "https://butiken.se", "")


def test_pastar_aldrig_full_forenlighet():
    """Bedömningen bygger på en skanning som fångar en tredjedel av bristerna.

    Att skriva "helt förenlig" utifrån det är exakt det påstående som gav en
    amerikansk leverantör en miljonbot.
    """
    for sajt in (_sajt(), _sajt(_brist("label", 200, "critical"))):
        text = redogörelse_markdown(sajt)
        assert "helt förenlig" not in text.replace("inte betecknas som helt förenlig", "")
        assert "delvis förenlig" in text


def test_ren_sajt_beskrivs_fortfarande_som_delvis_forenlig():
    text = redogörelse_markdown(_sajt())
    assert "inga brister" in text.lower()
    assert "en tredjedel" in text


def test_kundens_uppgifter_fylls_aldrig_i_pa_gissning():
    """Ett dokument med påhittad kontaktväg är värre än inget dokument."""
    text = redogörelse_markdown(_sajt(_brist("label")))
    for platshållare in ("[adress]", "[nummer]", "[Organisationens namn]"):
        assert platshållare in text


def test_organisation_anvands_nar_den_anges():
    text = redogörelse_markdown(_sajt(_brist("label")), organisation="Butiken AB")
    assert "Butiken AB" in text
    assert "[Organisationens namn]" not in text


def test_brister_redovisas_pa_svenska_med_wcag():
    text = redogörelse_markdown(_sajt(_brist("image-alt", 12)))
    assert "Bilder saknar alternativtext" in text
    assert "12 element" in text
    assert "WCAG 1.1.1" in text


def test_namner_tillsynsmyndigheten():
    """Redogörelsen ska tala om vart man vänder sig om svaret uteblir."""
    text = redogörelse_markdown(_sajt(_brist("label")))
    assert "Post- och telestyrelsen" in text


def test_markerar_att_det_ar_ett_utkast():
    text = redogörelse_markdown(_sajt(_brist("label")))
    assert "Utkast" in text
    assert "innan publicering" in text
