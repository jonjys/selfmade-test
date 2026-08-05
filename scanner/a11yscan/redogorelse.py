"""Genererar ett utkast till tillgänglighetsredogörelse.

Offerten lovar underlag till den redogörelse lagen kräver. Det här är det
underlaget.

Redogörelsen är ett dokument kunden publicerar på sin egen sajt. Den ska
beskriva hur tillgänglig tjänsten är, vad som inte fungerar, hur man påtalar
brister och vart man vänder sig om man inte får svar.

Två saker som styr utformningen:

* **Vi fyller aldrig i kundens uppgifter åt dem.** Kontaktväg och datum är
  markerade med hakparenteser. Ett dokument med påhittad e-postadress är värre
  än inget dokument, eftersom det ser klart ut.
* **Vi skriver aldrig "fullt förenlig".** Bedömningen bygger på en automatisk
  skanning som fångar ungefär en tredjedel av bristerna. Att påstå full
  efterlevnad utifrån det vore precis det påstående FTC bötfällde en
  amerikansk leverantör en miljon dollar för.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .report import beskriv
from .scan import Sajtresultat

# Tröskel för när vi kallar tjänsten "delvis förenlig" i stället för att
# beskriva bristerna som enstaka. Trubbig med avsikt — den exakta gränsen är
# en bedömningsfråga som kunden och deras jurist får landa.
MÅNGA_BRISTER = 25


def _förenlighet(sajt: Sajtresultat) -> tuple[str, str]:
    """Returnerar (grad, motivering) i redogörelsens språk.

    Graderna kommer från mallen för tillgänglighetsredogörelser: helt förenlig,
    delvis förenlig, inte förenlig. Vi använder aldrig "helt förenlig" — se
    modulens inledning.
    """
    if sajt.antal_brott == 0:
        return (
            "delvis förenlig",
            "Den automatiska genomgången hittade inga brister, men automatiska "
            "verktyg fångar bara omkring en tredjedel av det som kan vara fel. "
            "Tjänsten kan därför inte betecknas som helt förenlig utan en "
            "manuell granskning.",
        )
    if sajt.antal_brott < MÅNGA_BRISTER:
        return (
            "delvis förenlig",
            f"Genomgången hittade {sajt.antal_brott} element som avviker från "
            "kraven. Bristerna är avgränsade och redovisas nedan.",
        )
    return (
        "delvis förenlig",
        f"Genomgången hittade {sajt.antal_brott} element som avviker från "
        f"kraven, varav {sajt.kritiska} bedöms som allvarliga. Bristerna "
        "återkommer på flera sidor och redovisas nedan.",
    )


def redogörelse_markdown(sajt: Sajtresultat, *, organisation: str = "") -> str:
    """Bygger utkastet som markdown, redo att klistras in eller formateras om."""
    namn = organisation or f"[Organisationens namn]"
    grad, motivering = _förenlighet(sajt)

    # Gruppera bristerna per typ så att redogörelsen blir läsbar. Kunden ska
    # kunna stryka en rad när den är åtgärdad.
    per_regel: dict[str, int] = {}
    for ö in sajt.alla_överträdelser:
        per_regel[ö.regel_id] = per_regel.get(ö.regel_id, 0) + ö.antal

    rader = []
    for regel_id, antal in sorted(per_regel.items(), key=lambda x: -x[1]):
        ö = next(x for x in sajt.alla_överträdelser if x.regel_id == regel_id)
        rubrik, konsekvens, wcag = beskriv(ö)
        rader.append(f"- **{rubrik}** ({antal} element). {konsekvens} Krav: WCAG {wcag}.")

    brister = "\n".join(rader) if rader else (
        "- Inga brister hittades vid den automatiska genomgången."
    )

    return f"""# Tillgänglighetsredogörelse för {sajt.domän}

> **Utkast.** Fyll i uppgifterna inom hakparentes och stryk den här rutan
> innan publicering. Texten bygger på en automatisk genomgång och behöver
> kompletteras med en manuell granskning innan den är fullständig.

{namn} står bakom den här tjänsten. Vi vill att så många som möjligt ska
kunna använda den, och beskriver här hur {sajt.domän} uppfyller
tillgänglighetskraven, vilka brister vi känner till och hur du kan påtala dem.

## Hur tillgänglig är tjänsten?

Tjänsten är **{grad}** med kraven i lagen om vissa produkters och tjänsters
tillgänglighet. {motivering}

## Innehåll som inte är tillgängligt

Följande brister är kända och åtgärdas löpande:

{brister}

## Vad vi gör åt det

[Beskriv planen. Exempel: "Vi åtgärdar de allvarligaste bristerna under
[kvartal] och räknar med att vara klara [datum]."]

## Rapportera brister

Upptäcker du något som inte fungerar, hör av dig så åtgärdar vi det:

- E-post: [adress]
- Telefon: [nummer]

Vi svarar normalt inom [antal] arbetsdagar.

## Om du inte är nöjd med vårt svar

Post- och telestyrelsen har tillsyn över kraven. Är du inte nöjd med hur vi
hanterat din synpunkt kan du anmäla det till PTS.

## Hur vi har testat tjänsten

Bedömningen bygger på en automatisk genomgång av {len(sajt.lyckade_sidor)} sidor
mot WCAG 2.1 nivå AA, den nivå standarden EN 301 549 hänvisar till.
Automatiska verktyg fångar omkring en tredjedel av alla tillgänglighetsbrister;
resterande kräver manuell testning med skärmläsare och tangentbord.
[Komplettera med datum och omfattning för den manuella granskningen.]

Redogörelsen upprättades den {date.today().isoformat()} och senast uppdaterad
samma dag.
"""


def skriv_redogörelse(
    sajt: Sajtresultat, sökväg: Path, *, organisation: str = ""
) -> Path:
    sökväg.parent.mkdir(parents=True, exist_ok=True)
    sökväg.write_text(
        redogörelse_markdown(sajt, organisation=organisation), encoding="utf-8"
    )
    return sökväg
