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
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from .report import beskriv, första_meningen
from .rules import slå_upp
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
    steg: str = "1_forsta"
    skicka_efter_dagar: int = 0


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

    # Ingen av de formulerade krokarna fanns. Då tar vi den allvarligaste
    # bristen, men bara om den har en svensk beskrivning — annars hamnar ett
    # rått regel-id som "aria-required-parent" i ämnesraden på ett säljmejl,
    # vilket ser ut som ett buggigt utskick snarare än en observation.
    for ö in sajt.värsta(5):
        if slå_upp(ö.regel_id):
            return ö, beskriv(ö)[0].lower()

    värsta = sajt.värsta(1)
    if värsta:
        return värsta[0], "tillgängligheten brister på flera punkter"
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


def skriv_uppföljning1(sajt: Sajtresultat, avsändare: str) -> Utkast | None:
    """Uppföljning efter fyra dagar.

    En uppföljning som bara säger "hör av mig igen" är värdelös. Den här
    tillför en ny uppgift — vad bristerna innebär i uteblivna köp — och är
    kortare än det första mejlet. Kortare uppföljningar svaras oftare på.
    """
    if not sajt.genomförd or not sajt.alla_överträdelser:
        return None
    _, krok_text = _välj_krok(sajt)

    brödtext = f"""Hej igen,

Jag hörde av mig i förra veckan om tillgängligheten på {sajt.domän}.

En sak som kan vara värd att veta: ungefär var femte person har någon form
av funktionsnedsättning som påverkar hur de använder en webbplats. När
{krok_text} handlar det inte bara om lagkrav, utan om kunder som lägger
varor i varukorgen och inte kommer vidare.

Rapporten ligger kvar och tar två minuter att skicka. Säg till om ni vill ha
den.

Vänliga hälsningar
{avsändare}

--
Vill ni inte höra från mig igen, svara "nej tack" så stryker jag er.
"""
    return Utkast(
        domän=sajt.domän,
        ämne=f"Re: {sajt.domän}: {krok_text}",
        brödtext=brödtext,
        allvarliga=sajt.kritiska,
        krok=krok_text,
        steg="2_uppfoljning",
        skicka_efter_dagar=4,
    )


def skriv_avslut(sajt: Sajtresultat, avsändare: str) -> Utkast | None:
    """Sista mejlet, efter tio dagar.

    Att uttryckligen släppa taget ger ofta fler svar än ännu en påminnelse.
    Mottagaren slipper dålig samvete och svarar antingen "ja, hör av dig i
    höst" eller ingenting — båda är användbara besked.
    """
    if not sajt.genomförd or not sajt.alla_överträdelser:
        return None
    _, krok_text = _välj_krok(sajt)

    brödtext = f"""Hej,

Jag har hört av mig ett par gånger om {sajt.domän} utan att få svar, så jag
utgår från att det inte är aktuellt just nu. Helt i sin ordning — jag slutar
höra av mig.

Skulle det bli aktuellt, till exempel om ni gör om kassan eller får en fråga
från en myndighet, ligger skanningen kvar hos mig och jag skickar den gärna.

Lycka till med butiken.

{avsändare}
"""
    return Utkast(
        domän=sajt.domän,
        ämne=f"Re: {sajt.domän}: {krok_text}",
        brödtext=brödtext,
        allvarliga=sajt.kritiska,
        krok=krok_text,
        steg="3_avslut",
        skicka_efter_dagar=10,
    )


def skriv_leverans(sajt: Sajtresultat, avsändare: str) -> Utkast | None:
    """Mejlet som skickas när någon svarat ja på den kostnadsfria rapporten.

    Det här är det viktigaste mejlet i hela sekvensen, för det är här den
    betalda granskningen säljs. Rapporten levereras utan motkrav, och
    erbjudandet ligger sist och lågmält — den som just fått något gratis
    reagerar illa på ett hårt avslut.
    """
    if not sajt.genomförd:
        return None
    timmar = max(1, round(sajt.antal_brott * 10 / 60))

    brödtext = f"""Hej,

Här kommer rapporten för {sajt.domän}. Den är en fil — öppna i webbläsaren
eller skriv ut till PDF.

Kort sammanfattning: {sajt.antal_brott} element bryter mot WCAG 2.1 AA, varav
{sajt.kritiska} är allvarliga eller kritiska. Grovt räknat handlar det om
{timmar} timmars utvecklingsarbete att åtgärda merparten. Bristerna ligger
sorterade med de allvarligaste först, så det går att börja uppifrån.

Två saker att vara medveten om:

Rapporten bygger på en automatisk skanning, och sådana hittar ungefär en
tredjedel av alla brister. Resten kräver att någon testar manuellt med
skärmläsare och enbart tangentbord.

Den är heller inget juridiskt utlåtande. Den visar var det tekniskt brister
mot standarden.

Vill ni ha den fullständiga bilden gör jag en manuell granskning för
19 900 kr: hela kassaflödet testat med skärmläsare, en åtgärdslista er
utvecklare kan jobba efter, och underlag till den tillgänglighetsredogörelse
lagen kräver.

Ingen brådska. Hör av er om det är intressant, annars hoppas jag rapporten
kommer till nytta som den är.

Vänliga hälsningar
{avsändare}
"""
    return Utkast(
        domän=sajt.domän,
        ämne=f"Rapporten för {sajt.domän}",
        brödtext=brödtext,
        allvarliga=sajt.kritiska,
        krok="leverans",
        steg="4_leverans",
    )


SEKVENS = (skriv_utkast, skriv_uppföljning1, skriv_avslut, skriv_leverans)


def skriv_utkastfiler(
    resultat: list[Sajtresultat],
    katalog: Path,
    avsändare: str,
    avsändaradress: str = "",
) -> list[Path]:
    """Skriver hela mejlsekvensen per sajt, en katalog per domän.

    Fyra filer: första utskicket, uppföljning efter fyra dagar, avslut efter
    tio, och leveransmejlet att skicka när någon svarat ja. De tre första är
    en tidsplan, det fjärde ligger och väntar tills det behövs.
    """
    katalog.mkdir(parents=True, exist_ok=True)
    skrivna: list[Path] = []

    for sajt in resultat:
        sajtkatalog = katalog / sajt.domän.replace(".", "_").replace(":", "_")
        for bygg in SEKVENS:
            utkast = bygg(sajt, avsändare)
            if utkast is None:
                continue

            meddelande = EmailMessage()
            meddelande["Subject"] = utkast.ämne
            if avsändaradress:
                meddelande["From"] = avsändaradress
            # Mottagaren fylls i för hand. Vi gissar aldrig en adress.
            meddelande["To"] = ""
            meddelande.set_content(utkast.brödtext)

            sajtkatalog.mkdir(parents=True, exist_ok=True)
            sökväg = sajtkatalog / f"{utkast.steg}.eml"
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
