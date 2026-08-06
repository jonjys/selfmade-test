"""Lås fast publiceringskonfigurationen.

Bakgrunden är ett konkret fel: `vercel.json` sade `"framework": "nextjs"`
medan Next-appen ligger i `web/` och repo-roten saknar `package.json`.
Bygget gick igenom lokalt — kommandona i filen var rätt — men Vercels
Next-förinställning letar efter appen i projektroten och deployen föll.

Det som gör felet värt ett test är att det inte syns på något annat sätt än
en röd bock hos en extern tjänst. Testsviten var grön hela tiden.
"""

import json
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent.parent
KONFIG = ROT / "vercel.json"


@pytest.fixture(scope="module")
def konfig() -> dict:
    return json.loads(KONFIG.read_text(encoding="utf-8"))


def test_konfigen_finns_och_är_giltig_json(konfig):
    assert isinstance(konfig, dict)


def test_utkatalogen_är_den_next_faktiskt_skriver_till(konfig):
    """outputDirectory måste peka på Next-appens exportkatalog.

    Pekar den fel publiceras ingenting, och Vercel svarar 404 på en deploy
    som rapporterades som lyckad.
    """
    assert konfig["outputDirectory"] == "web/out"
    assert (ROT / "web" / "next.config.ts").exists()


def test_kommandona_körs_i_katalogen_där_package_json_ligger(konfig):
    for nyckel in ("installCommand", "buildCommand"):
        assert konfig[nyckel].startswith("cd web &&"), nyckel
    assert (ROT / "web" / "package.json").exists()


def test_ingen_ramverksförinställning_utan_package_json_i_roten(konfig):
    """Förinställningen får bara sättas om appen ligger där den letar.

    Så länge roten saknar package.json ska framework vara null, annars
    försöker Vercel köra Next-detektering i fel katalog.
    """
    if not (ROT / "package.json").exists():
        assert konfig["framework"] is None, (
            "vercel.json sätter en ramverksförinställning men repo-roten "
            "saknar package.json — Next-appen ligger i web/."
        )


def test_snedstreck_i_slutet_stämmer_med_next_konfigurationen(konfig):
    """Vercel och Next måste vara överens om URL:ernas form.

    Next exporterar `status/<domän>/index.html` med trailingSlash, och länkar
    internt till adresser med avslutande snedstreck. Säger Vercel något annat
    får varje sådan länk en onödig omdirigering — eller en loop.
    """
    next_konfig = (ROT / "web" / "next.config.ts").read_text(encoding="utf-8")
    next_har_snedstreck = "trailingSlash: true" in next_konfig
    assert konfig.get("trailingSlash") is next_har_snedstreck
    assert "cleanUrls" not in konfig, (
        "cleanUrls tar bort .html och krockar med trailingSlash."
    )
