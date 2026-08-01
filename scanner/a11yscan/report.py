"""Genererar den svenska rapporten och lead-listan.

Rapporten är produkten. Skanningen är bara råvaran — axe-core kan vem som helst
köra. Det som går att ta betalt för är att en vd läser tre stycken och förstår
vad det kostar att inte göra något.

Två utdata:
  * en kort minirapport per sajt, avsedd att bifogas i ett första mejl
  * en sammanställd CSV över alla skannade sajter, sorterad efter hur illa det
    ser ut — det är säljlistan
"""

from __future__ import annotations

import csv
from pathlib import Path

from .rules import IMPACT_SV, slå_upp
from .scan import Sajtresultat, Överträdelse

# Riktvärde för manuell granskning. Automatiska verktyg hittar ungefär en
# tredjedel av bristerna, vilket är väl dokumenterat. Vi skriver ut det i
# rapporten i stället för att låtsas att skanningen är heltäckande — annars
# bygger vi samma trovärdighetsproblem som overlay-branschen har.
AUTOMATISK_TÄCKNING = 0.35


def _beskriv(ö: Överträdelse) -> tuple[str, str, str]:
    """Returnerar (rubrik, konsekvens, wcag) på svenska med rimlig fallback."""
    info = slå_upp(ö.regel_id)
    if info:
        return info.rubrik, info.konsekvens, info.wcag
    return (
        ö.regel_id,
        ö.beskrivning or "Brist mot WCAG 2.1 AA. Kräver manuell bedömning.",
        "WCAG 2.1 AA",
    )


def _sidlista(sajt: Sajtresultat) -> str:
    """Namnger vilka sidtyper som faktiskt gick att läsa.

    Att skriva ut antalet försökta sidor vore missvisande — hittar vi inte
    varukorgen ska rapporten säga det, inte räkna med den.
    """
    typer = [s.sidtyp.lower() for s in sajt.lyckade_sidor]
    if not typer:
        return "inga sidor kunde läsas"
    if len(typer) == 1:
        return typer[0]
    return ", ".join(typer[:-1]) + " och " + typer[-1]


def minirapport(sajt: Sajtresultat) -> str:
    """Kort rapport för det första mejlet. Tre värsta bristerna, inget mer."""
    if not sajt.genomförd:
        orsak = sajt.fel or "ingen sida kunde läsas in"
        return f"# {sajt.domän}\n\nSkanningen kunde inte genomföras: {orsak}\n"

    rader = [
        f"# Tillgänglighetsgranskning: {sajt.domän}",
        "",
        f"Automatisk skanning av {len(sajt.lyckade_sidor)} sidor mot WCAG 2.1 AA, "
        "den nivå EN 301 549 och tillgänglighetslagen hänvisar till "
        f"({_sidlista(sajt)}).",
        "",
        f"**{sajt.antal_brott} element** bryter mot kraven, varav "
        f"**{sajt.kritiska}** är allvarliga eller kritiska.",
        "",
        "## De tre allvarligaste",
        "",
    ]

    for i, ö in enumerate(sajt.värsta(3), start=1):
        rubrik, konsekvens, wcag = _beskriv(ö)
        rader += [
            f"### {i}. {rubrik}",
            "",
            f"- **Allvarlighetsgrad:** {IMPACT_SV.get(ö.impact, ö.impact)}",
            f"- **Antal element:** {ö.antal}",
            f"- **Var:** {ö.sidtyp} ({ö.url})",
            f"- **Krav:** WCAG {wcag}",
            "",
            konsekvens,
            "",
        ]
        if ö.exempel_html:
            rader += ["```html", ö.exempel_html, "```", ""]

    uppskattat = int(sajt.antal_brott / AUTOMATISK_TÄCKNING)
    rader += [
        "## Viktig avgränsning",
        "",
        "Den här skanningen är automatisk. Automatiska verktyg fångar ungefär "
        f"en tredjedel av alla brister — resterande kräver manuell testning med "
        f"skärmläsare och tangentbord. Den verkliga siffran ligger sannolikt "
        f"närmare {uppskattat} element.",
        "",
        "Skanningen är heller inte ett juridiskt utlåtande. Den visar var det "
        "sannolikt brister, inte om en tillsynsmyndighet skulle ingripa.",
        "",
    ]
    return "\n".join(rader)


def skriv_minirapporter(resultat: list[Sajtresultat], katalog: Path) -> list[Path]:
    katalog.mkdir(parents=True, exist_ok=True)
    skrivna = []
    for sajt in resultat:
        sökväg = katalog / f"{sajt.domän.replace('.', '_')}.md"
        sökväg.write_text(minirapport(sajt), encoding="utf-8")
        skrivna.append(sökväg)
    return skrivna


def skriv_leadlista(resultat: list[Sajtresultat], sökväg: Path) -> Path:
    """CSV sorterad efter antal allvarliga brister. Det här är säljlistan."""
    sökväg.parent.mkdir(parents=True, exist_ok=True)
    rader = sorted(
        (s for s in resultat if s.genomförd),
        key=lambda s: (-s.kritiska, -s.antal_brott),
    )
    with sökväg.open("w", newline="", encoding="utf-8") as f:
        skrivare = csv.writer(f)
        skrivare.writerow(
            ["domän", "startadress", "allvarliga_brott", "totalt_brott",
             "skannade_sidor", "värsta_bristen"]
        )
        for s in rader:
            värsta = s.värsta(1)
            skrivare.writerow([
                s.domän,
                s.startadress,
                s.kritiska,
                s.antal_brott,
                len(s.sidor),
                _beskriv(värsta[0])[0] if värsta else "",
            ])
    return sökväg
