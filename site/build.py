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
REPOROT = ROT.parent
KÄLLA = ROT / "index.src.html"

# Den färdiga sidan läggs i public/ och checkas in. Vercel och de flesta andra
# statiska värdar serverar den katalogen utan byggsteg, vilket betyder att
# publiceringen inte kan gå sönder av att en byggmiljö saknar Python.
MÅL = REPOROT / "public" / "index.html"

# Fragmentet är bara till för plattformar som tillhandahåller egen skalett.
# Det behöver inte checkas in.
MÅL_FRAGMENT = ROT / "artifact.html"

TYPSNITT = {
    "@FONT_NEWSREADER@": ROT / "fonts" / "newsreader.woff2",
    "@FONT_PUBLICSANS@": ROT / "fonts" / "publicsans.woff2",
}

# Utan de här raderna renderar en mobil sidan i 980 pixlars bredd och gissar
# teckenkodningen till latin-1, vilket gör åäö till skräptecken. Fragmentet
# som publiceras som Artifact får dem från plattformens egen skalett, men en
# fil som ska ligga på ett vanligt webbhotell måste bära dem själv.
SKELETT = """<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{huvud}</head>
<body>
{kropp}</body>
</html>
"""


def _bädda_in_typsnitt(html: str) -> str:
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
    return html


def _dela_upp(fragment: str) -> tuple[str, str]:
    """Skiljer ut det som hör hemma i head från resten.

    Källfilen är skriven som ett fragment, men titeln hör hemma i head i ett
    fullständigt dokument. Utan det hamnar <title> i body, där webbläsaren
    visserligen ändå plockar upp den, men dokumentet blir ogiltigt.
    """
    huvud: list[str] = []
    kropp = fragment
    start = kropp.find("<title>")
    if start != -1:
        slut = kropp.find("</title>", start)
        if slut != -1:
            slut += len("</title>")
            huvud.append(kropp[start:slut])
            kropp = (kropp[:start] + kropp[slut:]).lstrip("\n")
    return ("\n".join(huvud) + "\n" if huvud else ""), kropp


def bygg() -> tuple[Path, Path]:
    """Bygger två filer.

    index.html är ett fullständigt dokument att lägga på ett webbhotell eller
    öppna direkt i en telefon. artifact.html är samma innehåll som fragment,
    för publicering där plattformen tillhandahåller skalett.
    """
    fragment = _bädda_in_typsnitt(KÄLLA.read_text(encoding="utf-8"))

    MÅL_FRAGMENT.write_text(fragment, encoding="utf-8")

    huvud, kropp = _dela_upp(fragment)
    MÅL.parent.mkdir(parents=True, exist_ok=True)
    MÅL.write_text(SKELETT.format(huvud=huvud, kropp=kropp), encoding="utf-8")

    return MÅL, MÅL_FRAGMENT


if __name__ == "__main__":
    fullständig, fragment = bygg()
    for sökväg, vad in ((fullständig, "fullständig sida"), (fragment, "fragment")):
        print(f"Skrev {sökväg.name:<14} {sökväg.stat().st_size // 1024:>4} kB  ({vad})")
