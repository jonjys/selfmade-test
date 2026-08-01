#!/usr/bin/env python3
"""Bygger index.html genom att bädda in typsnitten i källfilen.

Typsnitten måste ligga inline som data-URI. Den publicerade sidan körs under
en strikt CSP som blockerar externa värdar, så en länk till ett typsnitts-CDN
skulle tyst falla tillbaka på systemtypsnitt och hela typografin vore borta.

Filerna i fonts/ är subsettade till de tecken sidan använder, inklusive å ä ö,
och Newsreader är låst till en optisk storlek. Det tar dem från 132 kB till
35 kB.

    python3 site/build.py
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent
KÄLLA = ROT / "index.src.html"
MÅL = ROT / "index.html"

TYPSNITT = {
    "@FONT_NEWSREADER@": ROT / "fonts" / "newsreader.woff2",
    "@FONT_PUBLICSANS@": ROT / "fonts" / "publicsans.woff2",
}


def bygg() -> Path:
    html = KÄLLA.read_text(encoding="utf-8")

    for platshållare, sökväg in TYPSNITT.items():
        if not sökväg.exists():
            sys.exit(f"Typsnittet saknas: {sökväg}")
        if platshållare not in html:
            sys.exit(f"Platshållaren {platshållare} finns inte i {KÄLLA.name}")
        html = html.replace(
            platshållare,
            base64.b64encode(sökväg.read_bytes()).decode("ascii"),
        )

    kvar = [p for p in TYPSNITT if p in html]
    if kvar:
        sys.exit(f"Platshållare kvar efter bygget: {kvar}")

    MÅL.write_text(html, encoding="utf-8")
    return MÅL


if __name__ == "__main__":
    mål = bygg()
    print(f"Skrev {mål} ({mål.stat().st_size // 1024} kB)")
