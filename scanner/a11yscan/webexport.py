"""Exporterar skanningsresultat till webbappens datafil.

Kundens statussida är det som gör prenumerationen värd att behålla. Utan den
märks övervakningen bara när något gått sönder, och en tjänst som hör av sig
enbart med dåliga nyheter känns som en kostnad.

Filen skrivs till web/data/kunder.json och checkas in. Webbappen är statiskt
exporterad, så datan bakas in vid bygget — ingen databas, ingen server, inget
som kan gå sönder klockan tre på natten.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .bevakning import Förändring, _per_regel
from .report import beskriv, första_meningen
from .scan import Sajtresultat

# Hur många mätpunkter som sparas per kund. Fler säger inget mer på en
# veckoskanning, och filen ska vara liten nog att checka in.
HISTORIK_LÄNGD = 26


def _brister(sajt: Sajtresultat) -> list[dict]:
    """En rad per regeltyp, med den svenska beskrivningen."""
    per_regel: dict[str, dict] = {}
    for ö in sajt.alla_överträdelser:
        post = per_regel.get(ö.regel_id)
        if post:
            post["antal"] += ö.antal
            continue
        rubrik, konsekvens, wcag = beskriv(ö)
        per_regel[ö.regel_id] = {
            "regelId": ö.regel_id,
            "rubrik": rubrik,
            # Bara första meningen. Den längre texten resonerar ibland om
            # skanningsverktyg, vilket hör hemma i vår rapport men inte på
            # kundens egen statussida.
            "konsekvens": första_meningen(konsekvens) + ".",
            "wcag": wcag,
            "allvarlighet": ö.impact,
            "antal": ö.antal,
            "sidtyp": ö.sidtyp,
        }

    ordning = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
    return sorted(
        per_regel.values(),
        key=lambda b: (ordning.get(b["allvarlighet"], 9), -b["antal"]),
    )


def uppdatera_webbdata(
    resultat: list[Sajtresultat],
    sökväg: Path,
    *,
    ändringar: dict[str, Förändring] | None = None,
    namn: dict[str, str] | None = None,
) -> Path:
    """Skriver eller uppdaterar datafilen webbappen läser.

    Historiken bevaras mellan körningar. En misslyckad skanning skrivs aldrig
    in — annars skulle ett driftavbrott hos kunden se ut som en dramatisk
    förbättring på deras egen statussida.
    """
    befintlig: dict[str, dict] = {}
    if sökväg.exists():
        for post in json.loads(sökväg.read_text(encoding="utf-8")):
            befintlig[post["doman"]] = post

    idag = date.today().isoformat()

    for sajt in resultat:
        if not sajt.genomförd:
            continue

        post = befintlig.get(sajt.domän, {})
        historik = post.get("historik", [])
        # Skriv över dagens punkt i stället för att lägga till en till, så att
        # en omkörning samma dag inte ser ut som två veckors utveckling.
        historik = [h for h in historik if h["datum"] != idag]
        historik.append(
            {
                "datum": idag,
                "totalt": sajt.antal_brott,
                "allvarliga": sajt.kritiska,
            }
        )

        ändring = (ändringar or {}).get(sajt.domän)
        befintlig[sajt.domän] = {
            "doman": sajt.domän,
            "namn": (namn or {}).get(sajt.domän, post.get("namn", sajt.domän)),
            "senastSkannad": idag,
            "totalt": sajt.antal_brott,
            "allvarliga": sajt.kritiska,
            "historik": historik[-HISTORIK_LÄNGD:],
            "brister": _brister(sajt),
            "nya": sorted(ändring.nya) if ändring else [],
            "lagade": sorted(ändring.lagade) if ändring else [],
        }

    sökväg.parent.mkdir(parents=True, exist_ok=True)
    sökväg.write_text(
        json.dumps(
            sorted(befintlig.values(), key=lambda p: -p["allvarliga"]),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return sökväg
