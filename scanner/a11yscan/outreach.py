"""Genererar personliga säljmejl ur skanningsresultat.

Det här är den del som faktiskt hämtar in pengar. Skannern hittar fel,
rapporten förklarar dem — men ingen betalar förrän någon har fått ett mejl som
namnger något konkret på deras egen sajt.

Två principer styr utformningen:

* **Inget skickas automatiskt.** Modulen skriver utkast till .eml-filer som
  öppnas i vanlig e-postklient. Kallt utskick mot fel mottagare skadar
  varumärket mer än ett uteblivet mejl, och varje utkast ska läsas av en
  människa innan det går iväg.
* **Mejlet leder med en observation, inte ett erbjudande.** "Kassan går inte
  att slutföra med tangentbord" öppnas. "Vi erbjuder tillgänglighetstjänster"
  gör det inte.

Kallt B2B-utskick är tillåtet i Sverige, men mottagaren ska enkelt kunna säga
nej. Varje utkast innehåller därför en avanmälningsrad.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from .report import beskriv
from .scan import Sajtresultat, Överträdelse

# Vissa brister berättar en historia som en vd omedelbart förstår. Dem leder vi
# med, även om axe råkar rangordna något annat som allvarligare. Ordningen är
# vald efter hur konkret konsekvensen är för en e-handlare.
KROK = {
    "custom-click-handler-not-focusable":
        "delar av sidan går inte att använda utan mus",
    "label":
        "fält i formuläret saknar etikett",
    "custom-placeholder-som-etikett":
        "ledtexten i formuläret försvinner när kunden börjar skriva",
    "select-name":
        "storleks- och variantväljaren saknar etikett",
    "button-name":
        "knappar saknar läsbar text",
    "image-alt":
        "produktbilder saknar alternativtext",
    "custom-no-visible-focus":
        "det syns inte var man är när man navigerar med tangentbord",
    "color-contrast":
        "text har för låg kontrast för att gå att läsa",
    "meta-viewport":
        "det går inte att zooma på mobilen",
}


@dataclass
class Utkast:
    domän: str
    ämne: str
    brödtext: str
    allvarliga: int
    krok: str


def första_meningen(text: str) -> str:
    """Plockar ut första meningen utan att snubbla på förkortningar.

    En naiv split på punkt kapar "t.ex." mitt itu och ger en punktlista som
    slutar med "En ikonknapp utan text — t." Ett mejl med den sortens
    stympad text ser slarvigt ut, och slarv är det sista man vill signalera
    när man säljer granskningar.

    Vi bryter därför bara på en punkt som följs av blanksteg och versal.
    """
    text = text.strip()
    träff = re.search(r"\.(?=\s+[A-ZÅÄÖ])", text)
    if träff:
        return text[: träff.start()].strip()
    return text.rstrip(".").strip()


def _välj_krok(sajt: Sajtresultat) -> tuple[Överträdelse | None, str]:
    """Väljer den brist mejlet ska ledas med.

    Vi föredrar en brist med en konkret konsekvens framför den som axe råkar
    gradera högst — ett mejl som säger "12 element bryter mot WCAG 4.1.2"
    läses inte, ett som säger "kassan går inte att använda utan mus" läses.
    """
    hittade = {ö.regel_id: ö for ö in sajt.alla_överträdelser}
    for regel_id, formulering in KROK.items():
        if regel_id in hittade:
            return hittade[regel_id], formulering
    värsta = sajt.värsta(1)
    if värsta:
        return värsta[0], beskriv(värsta[0])[0].lower()
    return None, ""


def skriv_utkast(sajt: Sajtresultat, avsändare: str) -> Utkast | None:
    """Bygger ett mejlutkast för en sajt. None när det inte finns något att säga."""
    if not sajt.genomförd or not sajt.alla_överträdelser:
        return None

    krok_brist, krok_text = _välj_krok(sajt)
    if krok_brist is None:
        return None

    ämne = f"{sajt.domän}: {krok_text}"

    punkter = []
    for ö in sajt.värsta(3):
        rubrik, konsekvens, wcag = beskriv(ö)
        var = ö.sidtyp.lower()
        punkter.append(
            f"- {rubrik} ({ö.antal} st på {var}). {första_meningen(konsekvens)}."
        )

    brödtext = f"""Hej,

Jag testade {sajt.domän} med skärmläsare och enbart tangentbord. Kort version:
{krok_text}.

De tre allvarligaste sakerna:

{chr(10).join(punkter)}

Sedan juni 2025 omfattas e-handel av tillgänglighetslagen, och Post- och
telestyrelsen har inlett tillsyn mot ett antal svenska handlare. Kraven följer
WCAG 2.1 AA.

Vill ni ha hela listan? Den omfattar {sajt.antal_brott} element, med skärmbild
på varje och en prioriterad åtgärdsordning. Jag skickar den kostnadsfritt —
svara bara "ja" så kommer den.

Vänliga hälsningar
{avsändare}

--
Vill ni inte höra från mig igen, svara "nej tack" så stryker jag er.
Skanningen är automatisk och hittar ungefär en tredjedel av alla brister.
Den är inte ett juridiskt utlåtande.
"""

    return Utkast(
        domän=sajt.domän,
        ämne=ämne,
        brödtext=brödtext,
        allvarliga=sajt.kritiska,
        krok=krok_text,
    )


def skriv_utkastfiler(
    resultat: list[Sajtresultat],
    katalog: Path,
    avsändare: str,
    avsändaradress: str = "",
) -> list[Path]:
    """Skriver ett .eml-utkast per sajt. Filerna öppnas i vanlig e-postklient."""
    katalog.mkdir(parents=True, exist_ok=True)
    skrivna: list[Path] = []

    for sajt in resultat:
        utkast = skriv_utkast(sajt, avsändare)
        if utkast is None:
            continue

        meddelande = EmailMessage()
        meddelande["Subject"] = utkast.ämne
        if avsändaradress:
            meddelande["From"] = avsändaradress
        # Mottagaren fylls i för hand. Vi gissar aldrig en adress.
        meddelande["To"] = ""
        meddelande.set_content(utkast.brödtext)

        sökväg = katalog / f"{sajt.domän.replace('.', '_')}.eml"
        sökväg.write_bytes(bytes(meddelande))
        skrivna.append(sökväg)

    return skrivna


def skriv_ringlista(resultat: list[Sajtresultat], sökväg: Path, avsändare: str) -> Path:
    """CSV att jobba av uppifrån och ner, med öppningsreplik per rad."""
    sökväg.parent.mkdir(parents=True, exist_ok=True)
    rader = []
    for sajt in resultat:
        utkast = skriv_utkast(sajt, avsändare)
        if utkast:
            rader.append(utkast)
    rader.sort(key=lambda u: -u.allvarliga)

    with sökväg.open("w", newline="", encoding="utf-8") as f:
        skrivare = csv.writer(f)
        skrivare.writerow(["domän", "allvarliga", "öppningsreplik", "ämnesrad", "status"])
        for u in rader:
            skrivare.writerow([u.domän, u.allvarliga, u.krok, u.ämne, "ej kontaktad"])
    return sökväg
