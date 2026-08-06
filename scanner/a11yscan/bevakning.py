"""Löpande övervakning: jämför en ny skanning mot förra och larmar vid regression.

Det här är den enda delen av affären som tjänar pengar medan man sover.
Granskningen är en engångsleverans som kräver fyra till sex timmars manuellt
arbete. Övervakningen kör på schema, jämför mot förra körningen och hör av sig
bara när något faktiskt blivit sämre.

Tre beslut som formar modulen:

* **Tystnad är en funktion.** Ett veckomejl som säger "inget har ändrats"
  lär kunden att ignorera avsändaren, och en ignorerad avsändare sägs upp.
  Vi skickar bara när något förändrats.
* **Vi rapporterar även det som lagats.** Det är enda gången kunden ser vad
  de betalar för. En övervakning som bara larmar känns som en kostnad; en som
  också bekräftar framsteg känns som ett kvitto.
* **En sajt som inte gick att nå är inte en sajt utan brister.** Samma regel
  som i skannern. Utan den skulle ett driftavbrott hos kunden se ut som att
  alla fel plötsligt åtgärdats, och vi skulle gratulera dem till det.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .report import beskriv
from .scan import Sajtresultat, Överträdelse


@dataclass
class Förändring:
    """Skillnaden mellan två skanningar av samma sajt."""

    domän: str
    nya: dict[str, int] = field(default_factory=dict)
    lagade: dict[str, int] = field(default_factory=dict)
    ökade: dict[str, tuple[int, int]] = field(default_factory=dict)
    minskade: dict[str, tuple[int, int]] = field(default_factory=dict)
    föregående_datum: str = ""

    @property
    def har_regression(self) -> bool:
        """Sant när något blivit sämre. Det är det som motiverar ett mejl."""
        return bool(self.nya or self.ökade)

    @property
    def har_framsteg(self) -> bool:
        return bool(self.lagade or self.minskade)

    @property
    def något_hände(self) -> bool:
        return self.har_regression or self.har_framsteg


def _per_regel(sajt: Sajtresultat) -> dict[str, int]:
    summa: dict[str, int] = {}
    for ö in sajt.alla_överträdelser:
        summa[ö.regel_id] = summa.get(ö.regel_id, 0) + ö.antal
    return summa


def jämför(tidigare: dict[str, int], nu: Sajtresultat, *, sedan: str = "") -> Förändring:
    """Jämför en ny skanning mot en sparad utgångspunkt."""
    ändring = Förändring(domän=nu.domän, föregående_datum=sedan)
    nuvarande = _per_regel(nu)

    for regel_id, antal in nuvarande.items():
        gammalt = tidigare.get(regel_id, 0)
        if gammalt == 0:
            ändring.nya[regel_id] = antal
        elif antal > gammalt:
            ändring.ökade[regel_id] = (gammalt, antal)
        elif antal < gammalt:
            ändring.minskade[regel_id] = (gammalt, antal)

    for regel_id, antal in tidigare.items():
        if regel_id not in nuvarande:
            ändring.lagade[regel_id] = antal

    return ändring


class Utgångspunkt:
    """Sparar och läser den senaste skanningen per domän.

    En enkel JSON-fil räcker. En databas vore mer korrekt och skulle kräva
    drift, och drift är precis vad en produkt som ska tjäna pengar medan man
    sover inte ska ha mer av än nödvändigt.
    """

    def __init__(self, sökväg: Path) -> None:
        self.sökväg = sökväg
        self._data: dict[str, dict] = {}
        if sökväg.exists():
            self._data = json.loads(sökväg.read_text(encoding="utf-8"))

    def hämta(self, domän: str) -> tuple[dict[str, int], str]:
        post = self._data.get(domän)
        if not post:
            return {}, ""
        return post.get("regler", {}), post.get("datum", "")

    def uppdatera(self, sajt: Sajtresultat) -> None:
        """Sparar en skanning som ny utgångspunkt.

        Bara genomförda skanningar sparas. Skulle vi spara ett misslyckande
        som utgångspunkt vore nästa körning en falsk succéhistoria, där varje
        kvarvarande fel såg ut som nyupptäckt.
        """
        if not sajt.genomförd:
            return
        self._data[sajt.domän] = {
            "datum": date.today().isoformat(),
            "regler": _per_regel(sajt),
            "totalt": sajt.antal_brott,
        }

    def spara(self) -> Path:
        self.sökväg.parent.mkdir(parents=True, exist_ok=True)
        self.sökväg.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return self.sökväg


def _rad(regel_id: str, text: str) -> str:
    ö = Överträdelse(regel_id, "serious", 0, "", "", "")
    return f"- {beskriv(ö)[0]}: {text}"


def larmmejl(ändring: Förändring, sajt: Sajtresultat, avsändare: str) -> str | None:
    """Skriver larmet. None när inget hänt — då ska inget skickas.

    Mejlet leder med regressionen, eftersom det är den som kräver handling.
    Framstegen ligger sist som bekräftelse.
    """
    if not ändring.något_hände:
        return None

    delar = ["Hej,", ""]

    if ändring.har_regression:
        delar += [
            f"Veckans genomgång av {ändring.domän} hittade brister som inte fanns",
            "vid förra körningen. Det brukar betyda att en ny release återinfört",
            "något som tidigare var åtgärdat.",
            "",
        ]
        for regel_id, antal in sorted(ändring.nya.items(), key=lambda x: -x[1]):
            delar.append(_rad(regel_id, f"{antal} element, nytt sedan sist"))
        for regel_id, (förr, nu_) in sorted(
            ändring.ökade.items(), key=lambda x: -(x[1][1] - x[1][0])
        ):
            delar.append(_rad(regel_id, f"{förr} → {nu_} element"))
        delar.append("")
    else:
        delar += [
            f"Veckans genomgång av {ändring.domän} hittade inga nya brister.",
            "",
        ]

    if ändring.har_framsteg:
        delar.append("Det här har blivit bättre sedan sist:")
        for regel_id, antal in sorted(ändring.lagade.items(), key=lambda x: -x[1]):
            delar.append(_rad(regel_id, f"åtgärdat, var {antal} element"))
        for regel_id, (förr, nu_) in sorted(
            ändring.minskade.items(), key=lambda x: (x[1][1] - x[1][0])
        ):
            delar.append(_rad(regel_id, f"{förr} → {nu_} element"))
        delar.append("")

    delar += [
        f"Totalt just nu: {sajt.antal_brott} element, varav {sajt.kritiska}",
        "allvarliga eller kritiska.",
        "",
        "Fullständig rapport bifogas.",
        "",
        "Vänliga hälsningar",
        avsändare,
        "",
        "--",
        "Automatisk veckoskanning mot WCAG 2.1 AA. Den fångar ungefär en",
        "tredjedel av alla brister; resten kräver manuell testning.",
        "Vill ni ändra frekvens eller avsluta, svara på det här mejlet.",
    ]
    return "\n".join(delar)


def ämnesrad(ändring: Förändring) -> str:
    if ändring.har_regression:
        antal = sum(ändring.nya.values()) + sum(
            nu_ - förr for förr, nu_ in ändring.ökade.values()
        )
        return f"{ändring.domän}: {antal} nya tillgänglighetsbrister sedan förra veckan"
    return f"{ändring.domän}: åtgärdat sedan förra veckan"
