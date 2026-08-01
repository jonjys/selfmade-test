"""Regressionstest mot en testsajt med kända, avsiktliga brister.

Poängen är inte att verifiera axe-core — Deque testar sitt eget bibliotek. Det
som testas här är vår egen kedja: att reglerna vi filtrerar på är rätt, att
våra egna kontroller slår till, och framför allt att en sajt som inte gick att
nå aldrig kan se felfri ut.

Kör med:  python -m pytest tests/ -v
"""

from __future__ import annotations

import asyncio
import functools
import http.server
import socket
import threading
from pathlib import Path

import pytest

from a11yscan.report import minirapport
from a11yscan.scan import Sajtresultat, Sidresultat, Skanner, Överträdelse

FIXTURKATALOG = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def lokal_server():
    """Serverar testsajten på en ledig port under testets gång."""
    hanterare = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(FIXTURKATALOG)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), hanterare)
    port = server.server_address[1]
    tråd = threading.Thread(target=server.serve_forever, daemon=True)
    tråd.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="module")
def resultat(lokal_server) -> Sajtresultat:
    skanner = Skanner(samtidighet=1, timeout_ms=20_000)
    sajter = asyncio.run(
        skanner.skanna_många([f"{lokal_server}/trasig_butik.html"])
    )
    return sajter[0]


# De regler testsajten är byggd för att utlösa. Varje rad motsvarar en
# avsiktlig brist i fixturen.
FÖRVÄNTADE_REGLER = {
    "image-alt",
    "color-contrast",
    "link-name",
    "button-name",
    "select-name",
    "html-has-lang",
    "meta-viewport",
    "custom-click-handler-not-focusable",
    "custom-no-skip-link",
    "custom-no-visible-focus",
    "custom-placeholder-som-etikett",
}


def test_skanningen_genomfördes(resultat):
    assert resultat.genomförd, f"Skanningen misslyckades: {resultat.fel}"


def test_alla_avsiktliga_brister_hittas(resultat):
    funna = {ö.regel_id for ö in resultat.alla_överträdelser}
    saknade = FÖRVÄNTADE_REGLER - funna
    assert not saknade, f"Dessa brister missades: {sorted(saknade)}"


def test_heading_order_rapporteras_inte(resultat):
    """h1 följt av h3 är best-practice i axe, inte ett WCAG-krav.

    Vi ska inte rapportera det, eftersom falska positiva är det som gör att en
    kund slutar lita på rapporten.
    """
    funna = {ö.regel_id for ö in resultat.alla_överträdelser}
    assert "heading-order" not in funna


def test_kritiska_räknas_som_element_inte_regeltyper(resultat):
    assert resultat.antal_brott >= len(resultat.alla_överträdelser)
    assert resultat.kritiska > 0


def test_rapporten_är_på_svenska_och_nämner_avgränsningen(resultat):
    text = minirapport(resultat)
    assert "De tre allvarligaste" in text
    assert "Viktig avgränsning" in text
    # Rapporten får aldrig utge sig för att vara heltäckande.
    assert "en tredjedel" in text


def test_onåbar_sajt_ser_aldrig_felfri_ut():
    """Det farligaste möjliga felet: att säga 'allt är bra' om en död sajt."""
    trasig = Sajtresultat(
        domän="finns.inte",
        startadress="https://finns.inte",
        sidor=[Sidresultat(url="https://finns.inte", sidtyp="Startsida", fel="ERR_CONNECTION_RESET")],
        fel="Startsidan kunde inte läsas in: ERR_CONNECTION_RESET",
    )
    assert not trasig.genomförd
    assert trasig.antal_brott == 0
    assert "kunde inte genomföras" in minirapport(trasig)


def test_sajt_utan_lyckade_sidor_är_inte_genomförd():
    """Även utan fel på sajtnivå krävs minst en läst sida."""
    tom = Sajtresultat(
        domän="tom.se",
        startadress="https://tom.se",
        sidor=[Sidresultat(url="https://tom.se", sidtyp="Startsida", fel="HTTP 503")],
    )
    assert not tom.genomförd


def test_värsta_sorterar_kritiska_först():
    sajt = Sajtresultat(domän="x.se", startadress="https://x.se")
    sida = Sidresultat(url="https://x.se", sidtyp="Startsida")
    sida.överträdelser = [
        Överträdelse("minor-regel", "minor", 99, "Startsida", "https://x.se", ""),
        Överträdelse("kritisk-regel", "critical", 1, "Startsida", "https://x.se", ""),
        Överträdelse("allvarlig-regel", "serious", 5, "Startsida", "https://x.se", ""),
    ]
    sajt.sidor.append(sida)
    assert [ö.regel_id for ö in sajt.värsta(3)] == [
        "kritisk-regel",
        "allvarlig-regel",
        "minor-regel",
    ]
