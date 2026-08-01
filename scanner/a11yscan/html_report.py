"""Genererar den fristående HTML-rapporten.

Det här är produkten. Kunden betalar inte för en skanning — axe-core är gratis
och tar tio sekunder att köra. Kunden betalar för ett dokument som går att
skicka vidare till en styrelse, en utvecklare och en jurist utan att någon av
dem behöver fråga vad det betyder.

Rapporten är en enda fil med inbäddade bilder, så att den kan mejlas som
bilaga eller skrivas ut till PDF utan att något går sönder.
"""

from __future__ import annotations

import base64
import html
from datetime import date
from pathlib import Path

from .rules import IMPACT_SV, slå_upp
from .report import AUTOMATISK_TÄCKNING, beskriv
from .scan import Sajtresultat, Överträdelse

# Timkostnad för manuell åtgärd, använd för att uppskatta insats. Medvetet
# konservativ — det är bättre att kunden blir positivt överraskad.
MINUTER_PER_ELEMENT = {
    "critical": 12,
    "serious": 10,
    "moderate": 6,
    "minor": 3,
}

CSS = """
:root {
  --text: #1a1a1a; --dämpad: #5c5c5c; --linje: #e4e4e7; --bg: #ffffff;
  --kort: #fafafa; --kritisk: #b42318; --allvarlig: #c4320a;
  --måttlig: #b54708; --mindre: #667085; --accent: #12492f;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif;
}
.ark { max-width: 820px; margin: 0 auto; padding: 48px 24px 96px; }
header { border-bottom: 3px solid var(--accent); padding-bottom: 24px; margin-bottom: 40px; }
.etikett {
  font-size: 12px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: 8px;
}
h1 { font-size: 34px; line-height: 1.15; margin: 0 0 8px; letter-spacing: -.02em; }
.meta { color: var(--dämpad); font-size: 14px; }
.sammanfattning {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px; margin: 32px 0 40px;
}
.ruta {
  background: var(--kort); border: 1px solid var(--linje);
  border-radius: 10px; padding: 18px;
}
.ruta .tal { font-size: 30px; font-weight: 700; letter-spacing: -.02em; }
.ruta .text { font-size: 13px; color: var(--dämpad); margin-top: 2px; }
.ruta.varning .tal { color: var(--kritisk); }
h2 {
  font-size: 21px; margin: 44px 0 6px; padding-top: 20px;
  border-top: 1px solid var(--linje); letter-spacing: -.01em;
}
h2:first-of-type { border-top: none; padding-top: 0; }
.ingress { color: var(--dämpad); margin: 0 0 20px; }
.brist {
  border: 1px solid var(--linje); border-radius: 10px;
  padding: 22px; margin-bottom: 18px; background: var(--bg);
}
.brist-topp {
  display: flex; align-items: baseline; gap: 12px;
  flex-wrap: wrap; margin-bottom: 4px;
}
.brist h3 { font-size: 17px; margin: 0; letter-spacing: -.01em; }
.marke {
  font-size: 11px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; padding: 3px 8px; border-radius: 5px;
  border: 1px solid currentColor; white-space: nowrap;
}
.kritisk { color: var(--kritisk); } .allvarlig { color: var(--allvarlig); }
.måttlig { color: var(--måttlig); } .mindre { color: var(--mindre); }
.fakta {
  display: flex; gap: 20px; flex-wrap: wrap;
  font-size: 13px; color: var(--dämpad); margin: 10px 0 14px;
}
.fakta b { color: var(--text); font-weight: 600; }
.brist p { margin: 0 0 14px; }
figure { margin: 0 0 14px; }
figure img {
  max-width: 100%; border: 1px solid var(--linje);
  border-radius: 6px; display: block;
}
figcaption { font-size: 12px; color: var(--dämpad); margin-top: 6px; }
pre {
  background: #f6f6f7; border: 1px solid var(--linje); border-radius: 6px;
  padding: 12px 14px; overflow-x: auto; font-size: 12.5px; margin: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.notis {
  background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #d97706;
  border-radius: 8px; padding: 18px 20px; margin: 28px 0;
}
.notis h3 { margin: 0 0 8px; font-size: 15px; }
.notis p { margin: 0 0 8px; font-size: 14.5px; }
.notis p:last-child { margin-bottom: 0; }
table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 8px; }
th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--linje); }
th { font-size: 12px; text-transform: uppercase; letter-spacing: .06em; color: var(--dämpad); }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
footer {
  margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--linje);
  font-size: 13px; color: var(--dämpad);
}
@media print {
  .ark { padding: 0; max-width: none; }
  .brist { break-inside: avoid; }
}
@media (prefers-color-scheme: dark) {
  :root {
    --text: #ececec; --dämpad: #a1a1aa; --linje: #2e2e33; --bg: #17171a;
    --kort: #1e1e22; --kritisk: #f97066; --allvarlig: #fdA29b;
    --måttlig: #fec84b; --mindre: #98a2b3; --accent: #6ee7b7;
  }
  pre { background: #1e1e22; }
  .notis { background: #241c07; border-color: #4a3708; }
}
"""


def _bädda_in_bild(sökväg: Path) -> str:
    """Bäddar in en PNG som data-URI så att rapporten blir en enda fil."""
    data = base64.b64encode(sökväg.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _marke(impact: str) -> str:
    klass = {
        "critical": "kritisk",
        "serious": "allvarlig",
        "moderate": "måttlig",
        "minor": "mindre",
    }.get(impact, "mindre")
    return f'<span class="marke {klass}">{IMPACT_SV.get(impact, impact)}</span>'


def _uppskattad_insats(sajt: Sajtresultat) -> float:
    """Grov uppskattning av åtgärdstid i timmar.

    Bygger på antal element, inte antal regeltyper, eftersom det är elementen
    en utvecklare rör. Uppskattningen är avsiktligt trubbig och presenteras som
    en storleksordning, inte som en offert.
    """
    minuter = sum(
        ö.antal * MINUTER_PER_ELEMENT.get(ö.impact, 5)
        for ö in sajt.alla_överträdelser
    )
    return round(minuter / 60, 1)


def _brist_html(ö: Överträdelse, bildkatalog: Path | None) -> str:
    rubrik, konsekvens, wcag = beskriv(ö)
    delar = [
        '<div class="brist">',
        '<div class="brist-topp">',
        f"<h3>{html.escape(rubrik)}</h3>{_marke(ö.impact)}",
        "</div>",
        '<div class="fakta">',
        f"<span><b>{ö.antal}</b> element</span>",
        f"<span>{html.escape(ö.sidtyp)}</span>",
        f"<span>WCAG {html.escape(wcag)}</span>",
        "</div>",
        f"<p>{html.escape(konsekvens)}</p>",
    ]

    if ö.skärmbild and bildkatalog:
        bild = bildkatalog / ö.skärmbild
        if bild.exists():
            delar += [
                "<figure>",
                f'<img src="{_bädda_in_bild(bild)}" alt="Skärmbild av det felande elementet, markerat med röd ram">',
                "<figcaption>Elementet är markerat med röd ram.</figcaption>",
                "</figure>",
            ]

    if ö.exempel_html:
        delar.append(f"<pre><code>{html.escape(ö.exempel_html)}</code></pre>")

    delar.append("</div>")
    return "\n".join(delar)


def html_rapport(sajt: Sajtresultat, bildkatalog: Path | None = None) -> str:
    """Bygger en fristående HTML-rapport för en sajt."""
    if not sajt.genomförd:
        orsak = html.escape(sajt.fel or "ingen sida kunde läsas in")
        return (
            f"<style>{CSS}</style><div class='ark'><h1>{html.escape(sajt.domän)}</h1>"
            f"<p>Skanningen kunde inte genomföras: {orsak}</p></div>"
        )

    sorterade = sorted(
        sajt.alla_överträdelser,
        key=lambda ö: ({"critical": 0, "serious": 1, "moderate": 2, "minor": 3}.get(ö.impact, 9), -ö.antal),
    )
    uppskattat_verkligt = int(sajt.antal_brott / AUTOMATISK_TÄCKNING)
    timmar = _uppskattad_insats(sajt)

    # Sammanställning per sidtyp — visar var problemen sitter.
    per_sida: dict[str, tuple[int, int]] = {}
    for s in sajt.lyckade_sidor:
        brott = sum(ö.antal for ö in s.överträdelser)
        allvar = sum(
            ö.antal for ö in s.överträdelser if ö.impact in ("critical", "serious")
        )
        per_sida[s.sidtyp] = (allvar, brott)

    rader = "\n".join(
        f"<tr><td>{html.escape(typ)}</td>"
        f'<td class="num">{a}</td><td class="num">{b}</td></tr>'
        for typ, (a, b) in per_sida.items()
    )

    brister = "\n".join(_brist_html(ö, bildkatalog) for ö in sorterade)

    return f"""<style>{CSS}</style>
<div class="ark">
  <header>
    <div class="etikett">Tillgänglighetsgranskning</div>
    <h1>{html.escape(sajt.domän)}</h1>
    <div class="meta">
      Automatisk skanning mot WCAG 2.1 AA &middot; {date.today().isoformat()}
    </div>
  </header>

  <div class="sammanfattning">
    <div class="ruta varning">
      <div class="tal">{sajt.kritiska}</div>
      <div class="text">allvarliga eller kritiska element</div>
    </div>
    <div class="ruta">
      <div class="tal">{sajt.antal_brott}</div>
      <div class="text">element totalt</div>
    </div>
    <div class="ruta">
      <div class="tal">{len(sorterade)}</div>
      <div class="text">olika typer av brist</div>
    </div>
    <div class="ruta">
      <div class="tal">~{timmar} h</div>
      <div class="text">uppskattad åtgärdstid</div>
    </div>
  </div>

  <h2>Vad kraven säger</h2>
  <p class="ingress">
    Lagen om vissa produkters och tjänsters tillgänglighet trädde i kraft i juni
    2025 och omfattar e-handel. Kraven följer standarden EN 301 549, som i sin
    tur hänvisar till WCAG 2.1 nivå AA. Post- och telestyrelsen utövar tillsyn
    och kan besluta om förelägganden, vite och sanktionsavgifter.
  </p>

  <h2>Var bristerna sitter</h2>
  <table>
    <thead><tr><th>Sida</th><th class="num">Allvarliga</th><th class="num">Totalt</th></tr></thead>
    <tbody>{rader}</tbody>
  </table>

  <h2>Samtliga funna brister</h2>
  <p class="ingress">Sorterade efter allvarlighetsgrad. Åtgärda uppifrån.</p>
  {brister}

  <div class="notis">
    <h3>Vad den här rapporten inte är</h3>
    <p>
      Skanningen är automatisk. Automatiska verktyg fångar ungefär en tredjedel
      av alla tillgänglighetsbrister — resten kräver manuell testning med
      skärmläsare och tangentbord. Det verkliga antalet ligger sannolikt
      närmare <b>{uppskattat_verkligt} element</b>.
    </p>
    <p>
      Rapporten är inte ett juridiskt utlåtande och innebär inte att sajten
      uppfyller eller inte uppfyller lagens krav. Den visar var det sannolikt
      brister. Ingen leverantör kan lova efterlevnad utifrån en maskinell
      skanning, och den som gör det bör man vara försiktig med.
    </p>
  </div>

  <footer>
    Genererad med axe-core 4.10.2 (Deque Systems, MPL-2.0) samt fyra egna
    kontroller för tangentbordsnavigering.
  </footer>
</div>
"""


def skriv_html_rapporter(
    resultat: list[Sajtresultat], katalog: Path, bildkatalog: Path | None = None
) -> list[Path]:
    katalog.mkdir(parents=True, exist_ok=True)
    skrivna = []
    for sajt in resultat:
        sökväg = katalog / f"{sajt.domän.replace('.', '_')}.html"
        sökväg.write_text(html_rapport(sajt, bildkatalog), encoding="utf-8")
        skrivna.append(sökväg)
    return skrivna
