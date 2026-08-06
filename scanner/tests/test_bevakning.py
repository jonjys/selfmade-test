"""Tester för den löpande övervakningen.

Det här är den del av affären som körs utan att någon tittar på. Ett fel här
upptäcks inte av en människa som läser resultatet — det går rakt ut till en
betalande kund, eller uteblir tyst.
"""

from __future__ import annotations

from pathlib import Path

from a11yscan.bevakning import (
    Utgångspunkt,
    jämför,
    larmmejl,
    ämnesrad,
)
from a11yscan.scan import Sajtresultat, Sidresultat, Överträdelse


def _sajt(regler: dict[str, int], domän: str = "butiken.se") -> Sajtresultat:
    sida = Sidresultat(url=f"https://{domän}", sidtyp="Startsida")
    sida.överträdelser = [
        Överträdelse(r, "serious", n, "Startsida", f"https://{domän}", "")
        for r, n in regler.items()
    ]
    return Sajtresultat(domän=domän, startadress=f"https://{domän}", sidor=[sida])


def _trasig(domän: str = "butiken.se") -> Sajtresultat:
    return Sajtresultat(
        domän=domän,
        startadress=f"https://{domän}",
        sidor=[Sidresultat(url=f"https://{domän}", sidtyp="Startsida", fel="timeout")],
        fel="Startsidan kunde inte läsas in: timeout",
    )


def test_ingen_forandring_ger_inget_mejl():
    """Ett veckomejl som säger 'inget har ändrats' lär kunden att ignorera oss."""
    tidigare = {"image-alt": 4, "label": 2}
    ändring = jämför(tidigare, _sajt({"image-alt": 4, "label": 2}))
    assert not ändring.något_hände
    assert larmmejl(ändring, _sajt(tidigare), "T T") is None


def test_ny_brist_upptacks():
    ändring = jämför({"image-alt": 4}, _sajt({"image-alt": 4, "button-name": 3}))
    assert ändring.har_regression
    assert ändring.nya == {"button-name": 3}


def test_okat_antal_raknas_som_regression():
    ändring = jämför({"image-alt": 4}, _sajt({"image-alt": 9}))
    assert ändring.har_regression
    assert ändring.ökade == {"image-alt": (4, 9)}


def test_atgardad_brist_rapporteras():
    """Framstegen är enda gången kunden ser vad de betalar för."""
    ändring = jämför({"image-alt": 4, "label": 2}, _sajt({"image-alt": 4}))
    assert not ändring.har_regression
    assert ändring.har_framsteg
    assert ändring.lagade == {"label": 2}
    mejl = larmmejl(ändring, _sajt({"image-alt": 4}), "T T")
    assert mejl is not None
    assert "blivit bättre" in mejl


def test_mejlet_leder_med_regressionen():
    ändring = jämför(
        {"image-alt": 4, "label": 2},
        _sajt({"image-alt": 4, "button-name": 5}),
    )
    mejl = larmmejl(ändring, _sajt({"image-alt": 4, "button-name": 5}), "T T")
    assert mejl is not None
    regression = mejl.index("inte fanns")
    framsteg = mejl.index("blivit bättre")
    assert regression < framsteg, "handling ska stå före bekräftelse"


def test_amnesraden_beskriver_omfattningen():
    ändring = jämför({}, _sajt({"button-name": 3, "label": 2}))
    assert "5 nya" in ämnesrad(ändring)


def test_misslyckad_skanning_sparas_aldrig_som_utgangspunkt(tmp_path: Path):
    """Annars ser nästa körning ut som att allt plötsligt åtgärdats.

    En sajt som ligger nere skulle spara noll brister, och veckan därpå
    skulle varje kvarvarande fel rapporteras som nyupptäckt — samtidigt som
    kunden fått ett gratulationsmejl för fel som aldrig lagades.
    """
    punkt = Utgångspunkt(tmp_path / "bas.json")
    punkt.uppdatera(_sajt({"image-alt": 4}))
    punkt.uppdatera(_trasig())
    regler, _ = punkt.hämta("butiken.se")
    assert regler == {"image-alt": 4}


def test_utgangspunkten_overlever_omstart(tmp_path: Path):
    sökväg = tmp_path / "bas.json"
    punkt = Utgångspunkt(sökväg)
    punkt.uppdatera(_sajt({"image-alt": 4, "label": 1}))
    punkt.spara()

    igen = Utgångspunkt(sökväg)
    regler, datum = igen.hämta("butiken.se")
    assert regler == {"image-alt": 4, "label": 1}
    assert datum


def test_forsta_korningen_ger_inget_falskt_larm():
    """Utan utgångspunkt är varje brist 'ny' — men det är inte en regression.

    Den första körningen efter att en kund tecknat övervakning ska sätta
    utgångspunkten, inte skicka ett larm om allt som redan fanns när de
    beställde.
    """
    ändring = jämför({}, _sajt({"image-alt": 4}), sedan="")
    assert ändring.föregående_datum == ""
    # Anroparen ska kunna skilja på "första gången" och "regression".
    assert ändring.har_regression


def test_mejlet_har_alltid_avgransningen_och_avslutsvag():
    ändring = jämför({}, _sajt({"image-alt": 4}))
    mejl = larmmejl(ändring, _sajt({"image-alt": 4}), "T T")
    assert mejl is not None
    assert "en" in mejl and "tredjedel" in mejl
    assert "avsluta" in mejl
