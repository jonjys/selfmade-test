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

from .html_report import skriv_html_rapporter
from .report import skriv_leadlista, skriv_minirapporter
from .scan import Skanner, spara_json


def _läs_sajter(sökväg: Path) -> list[str]:
    adresser = []
    for rad in sökväg.read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if not rad or rad.startswith("#"):
            continue
        adresser.append(rad if rad.startswith("http") else f"https://{rad}")
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
    print(f"  Rapporter: {len(rapporter)} md + {len(html_rapporter)} html "
          f"i {args.ut / 'rapporter'}")
    print(f"  Leadlista: {lead}")

    if lyckade:
        print("\nVärst ute:")
        for s in sorted(lyckade, key=lambda x: -x.kritiska)[:10]:
            print(f"  {s.domän:<35} {s.kritiska:>4} allvarliga  ({s.antal_brott} totalt)")
    for s in misslyckade:
        print(f"  MISSLYCKADES {s.domän}: {s.fel[:80]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
