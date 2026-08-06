"""Kommandoradsgränssnitt.

    python -m a11yscan.cli --sajter sites.txt --ut resultat/
    python -m a11yscan.cli --url https://example.se
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from email.message import EmailMessage

from .bevakning import Utgångspunkt, jämför, larmmejl, ämnesrad
from .html_report import skriv_html_rapporter
from .offert import skriv_offert
from .redogorelse import skriv_redogörelse
from .outreach import skriv_ringlista, skriv_utkastfiler
from .report import skriv_leadlista, skriv_minirapporter
from .scan import Skanner, spara_json
from .webexport import uppdatera_webbdata


def _läs_sajter(sökväg: Path) -> list[str]:
    """Läser adresslistan och tar bort dubbletter.

    En dubblett i listan skannas två gånger och skriver över sin egen rapport
    och offert, så bara en av körningarna överlever — utan att något syns i
    utdata. Ordningen bevaras så att listan går att jobba av uppifrån.
    """
    adresser: list[str] = []
    sedda: set[str] = set()
    for rad in sökväg.read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if not rad or rad.startswith("#"):
            continue
        adress = rad if rad.startswith("http") else f"https://{rad}"
        nyckel = adress.rstrip("/").lower()
        if nyckel in sedda:
            continue
        sedda.add(nyckel)
        adresser.append(adress)
    return adresser


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Skannar sajter mot WCAG 2.1 AA och genererar svensk rapport."
    )
    källa = p.add_mutually_exclusive_group(required=True)
    källa.add_argument("--sajter", type=Path, help="Fil med en adress per rad")
    källa.add_argument("--url", help="Enskild adress att skanna")
    p.add_argument("--ut", type=Path, default=Path("resultat"), help="Utdatakatalog")
    p.add_argument("--samtidighet", type=int, default=3, help="Antal parallella sajter")
    p.add_argument("--timeout", type=int, default=30, help="Timeout per sida i sekunder")
    p.add_argument(
        "--utan-bilder",
        action="store_true",
        help="Hoppa över skärmbilder (snabbare vid stora körningar)",
    )
    p.add_argument(
        "--avsandare",
        default="",
        help="Ditt namn. Anges det genereras mejlutkast och ringlista.",
    )
    p.add_argument("--avsandaradress", default="", help="Din e-postadress i utkasten")
    p.add_argument(
        "--via-python",
        action="store_true",
        help="Tvinga hämtning via Pythons nätverksstack. Behövs normalt inte "
             "— skannern byter automatiskt när webbläsaren inte kommer ut.",
    )
    p.add_argument(
        "--bevaka",
        type=Path,
        metavar="BAS.JSON",
        help="Kör som löpande övervakning: jämför mot förra körningen, skriv "
             "larm bara när något förändrats, och uppdatera utgångspunkten.",
    )
    p.add_argument(
        "--webbdata",
        type=Path,
        metavar="KUNDER.JSON",
        help="Skriv kundernas statussidor till webbappens datafil "
             "(normalt web/data/kunder.json).",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    adresser = [args.url] if args.url else _läs_sajter(args.sajter)
    if not adresser:
        print("Inga adresser att skanna.", file=sys.stderr)
        return 1

    print(f"Skannar {len(adresser)} sajter med samtidighet {args.samtidighet}...")
    skanner = Skanner(
        samtidighet=args.samtidighet,
        timeout_ms=args.timeout * 1000,
        skärmbildskatalog=None if args.utan_bilder else args.ut / "skärmbilder",
        hämta_via_python=args.via_python,
    )
    resultat = asyncio.run(skanner.skanna_många(adresser))

    bildkatalog = None if args.utan_bilder else args.ut / "skärmbilder"
    spara_json(resultat, args.ut / "radata.json")
    rapporter = skriv_minirapporter(resultat, args.ut / "rapporter")
    html_rapporter = skriv_html_rapporter(resultat, args.ut / "rapporter", bildkatalog)
    lead = skriv_leadlista(resultat, args.ut / "leadlista.csv")

    lyckade = [r for r in resultat if r.genomförd]
    misslyckade = [r for r in resultat if not r.genomförd]

    print(f"\nKlart. {len(lyckade)} skannade, {len(misslyckade)} misslyckades.")
    if skanner._python_användes and not args.via_python:
        print("  (Webbläsaren kom inte ut — sidorna hämtades via Python i stället.)")
    print(f"  Rapporter: {len(rapporter)} md + {len(html_rapporter)} html "
          f"i {args.ut / 'rapporter'}")
    print(f"  Leadlista: {lead}")

    if args.avsandare:
        utkast = skriv_utkastfiler(
            resultat, args.ut / "utkast", args.avsandare, args.avsandaradress
        )
        ringlista = skriv_ringlista(resultat, args.ut / "ringlista.csv", args.avsandare)
        offerter = [
            skriv_offert(
                s,
                args.ut / "offerter" / f"{s.domän.replace('.', '_')}.html",
                mottagare=s.domän,
                avsändare=args.avsandare,
                kontakt=args.avsandaradress,
            )
            for s in resultat
            if s.genomförd
        ]
        redogörelser = [
            skriv_redogörelse(
                s, args.ut / "redogorelser" / f"{s.domän.replace('.', '_')}.md"
            )
            for s in resultat
            if s.genomförd
        ]
        print(f"  Mejlutkast: {len(utkast)} st i {args.ut / 'utkast'}")
        print(f"  Redogörelser: {len(redogörelser)} st i {args.ut / 'redogorelser'}")
        print(f"  Offerter: {len(offerter)} st i {args.ut / 'offerter'}")
        print(f"  Ringlista: {ringlista}")
        print("\n  Utkasten skickas INTE automatiskt. Öppna, läs, fyll i mottagare.")
        print("  Varje sajt har fyra mejl: första, uppföljning, avslut, leverans.")

    ändringar = _kör_bevakning(resultat, args) if args.bevaka else {}

    if args.webbdata:
        sökväg = uppdatera_webbdata(resultat, args.webbdata, ändringar=ändringar)
        print(f"  Webbdata: {sökväg}")

    if lyckade:
        print("\nVärst ute:")
        for s in sorted(lyckade, key=lambda x: -x.kritiska)[:10]:
            print(f"  {s.domän:<35} {s.kritiska:>4} allvarliga  ({s.antal_brott} totalt)")
    for s in misslyckade:
        print(f"  MISSLYCKADES {s.domän}: {s.fel[:80]}")

    return 0


def _kör_bevakning(resultat, args) -> dict:
    """Jämför mot förra körningen och skriver larm för det som förändrats.

    Utgångspunkten uppdateras även när inget larm skrivs, annars skulle en
    gradvis försämring aldrig överskrida tröskeln.
    """
    punkt = Utgångspunkt(args.bevaka)
    ändringar: dict = {}
    katalog = args.ut / "larm"
    skrivna = 0
    tysta = 0
    första = 0

    for sajt in resultat:
        if not sajt.genomförd:
            continue
        tidigare, sedan = punkt.hämta(sajt.domän)
        if not sedan:
            # Första körningen sätter utgångspunkten. Att larma om allt som
            # redan fanns när kunden beställde vore att fakturera dem för en
            # nyhet de själva känner till.
            punkt.uppdatera(sajt)
            första += 1
            continue

        ändring = jämför(tidigare, sajt, sedan=sedan)
        ändringar[sajt.domän] = ändring
        text = larmmejl(ändring, sajt, args.avsandare or "Övervakningen")
        if text:
            meddelande = EmailMessage()
            meddelande["Subject"] = ämnesrad(ändring)
            if args.avsandaradress:
                meddelande["From"] = args.avsandaradress
            meddelande["To"] = ""
            # Explicit quoted-printable. Utan det väljer Python 8bit när
            # texten innehåller tecken utanför ASCII, vilket är giltigt men
            # inte lika brett stött — och skillnaden syns först i mottagarens
            # klient, inte hos oss.
            meddelande.set_content(text, cte="quoted-printable")
            katalog.mkdir(parents=True, exist_ok=True)
            (katalog / f"{sajt.domän.replace('.', '_')}.eml").write_bytes(
                bytes(meddelande)
            )
            skrivna += 1
        else:
            tysta += 1
        punkt.uppdatera(sajt)

    punkt.spara()
    print(f"\nBevakning: {skrivna} larm, {tysta} oförändrade, "
          f"{första} nya under bevakning.")
    if skrivna:
        print(f"  Larm att granska och skicka: {katalog}")
    print(f"  Utgångspunkt: {args.bevaka}")
    return ändringar


if __name__ == "__main__":
    raise SystemExit(main())
