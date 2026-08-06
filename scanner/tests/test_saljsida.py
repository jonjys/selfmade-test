"""Kontrollera att sidan som publiceras faktiskt går att kontakta.

Bakgrunden är att startsidan i `web/` ett tag sålde tre prisnivåer, lovade
"svar inom ett dygn" — och inte hade någon knapp, något formulär eller någon
adress. Varje besökare som blev övertygad hade ingenstans att ta vägen.

Det är ett fel som inget bygge och ingen typkontroll upptäcker, eftersom
sidan är helt korrekt. Den är bara oanvändbar som säljsida.
"""

import re
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parent.parent.parent
WEBB = ROT / "web"


@pytest.fixture(scope="module")
def startsida() -> str:
    return (WEBB / "app" / "page.tsx").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def formulär() -> str:
    return (WEBB / "app" / "Skanforfragan.tsx").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def kontakt() -> str:
    return (WEBB / "lib" / "kontakt.ts").read_text(encoding="utf-8")


def test_startsidan_har_en_väg_till_förfrågan(startsida):
    assert "Skanforfragan" in startsida, (
        "Startsidan säljer en tjänst men har inget sätt att beställa den."
    )
    assert "#skanning" in startsida, "Ingen länk leder till formuläret."


def test_fältet_har_en_riktig_etikett(formulär):
    """Placeholder är ingen etikett.

    Den försvinner när någon börjar skriva och läses inte upp av alla
    skärmläsare. Ett tillgänglighetsföretag med ett oetiketterat fält har
    ingen produkt att sälja.
    """
    assert "<label" in formulär
    assert "htmlFor=" in formulär


def test_felmeddelandet_annonseras(formulär):
    """Ett fel som bara syns hjälper inte den som inte ser."""
    assert 'role="alert"' in formulär
    assert 'role="status"' in formulär
    assert "aria-invalid" in formulär
    assert "aria-describedby" in formulär


def test_länkar_i_löptext_är_understrukna(startsida, formulär):
    """WCAG 1.4.1: färg får inte vara enda skillnaden.

    Skannern hittade precis den bristen i den första versionen av den här
    sidan. Testet finns för att den inte ska smyga tillbaka.
    """
    for källa, namn in ((startsida, "page.tsx"), (formulär, "Skanforfragan.tsx")):
        # Bara a-taggar omfattas. Etiketter och siffror är också gröna, men
        # de är inte länkar och ska inte understrykas.
        for träff in re.finditer(r"<a\s[^>]*>", källa, re.DOTALL):
            tagg = träff.group(0)
            if "text-signal" in tagg:
                assert "underline" in tagg, (
                    f"{namn}: länk som bara skiljs ut på färg: {tagg}"
                )


def test_platshållaren_öppnar_aldrig_ett_mejlfönster(kontakt, formulär):
    """Så länge adressen är påhittad ska formuläret säga det.

    Alternativet — att öppna ett mejlfönster till hej@example.se — ser för
    besökaren ut som att tjänsten inte finns på riktigt.
    """
    assert "ÄR_KONFIGURERAD" in kontakt
    assert "example.se" in kontakt, "Platshållaren måste gå att känna igen."
    assert "if (!ÄR_KONFIGURERAD)" in formulär


def test_adressen_finns_på_ett_ställe(kontakt):
    """En adress som står på två ställen blir förr eller senare två adresser."""
    assert kontakt.count('= "hej@example.se"') == 1
    assert "NEXT_PUBLIC_MOTTAGARE" in kontakt


def test_readme_pekar_ut_båda_sidorna():
    text = (ROT / "README.md").read_text(encoding="utf-8")
    assert "web/lib/kontakt.ts" in text
    assert "site/index.src.html" in text
