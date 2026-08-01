"""Genererar en offert utifrån skanningsresultatet.

När någon svarat ja på den kostnadsfria rapporten och sagt att den betalda
granskningen är intressant, ska det gå minuter innan offerten ligger i deras
inkorg. En offert som dröjer tre dagar har förlorat hälften av sin kraft.

Offerten är avsiktligt kort och innehåller en fast prislapp. Fastpris vinner
mot timdebitering i det här segmentet, eftersom köparen inte kan bedöma hur
många timmar som krävs och därför tolkar timpris som obegränsad risk.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .html_report import CSS
from .scan import Sajtresultat

# Fasta priser. Ändra här, inte i mallen.
PRIS_GRANSKNING = 19_900
PRIS_OVERVAKNING_FRAN = 2_900
TIMPRIS_ATGARD = 1_150

GILTIGHET_DAGAR = 30


# Hårt mellanslag som tusentalsavgränsare. Svensk standard, och det hindrar
# att "19" och "900" hamnar på olika rader i en offert.
TUSENTAL = "\u00a0"


def kr(belopp: int) -> str:
    """Formaterar ett belopp enligt svensk konvention: 19 900, inte 19,900."""
    return f"{belopp:,}".replace(",", TUSENTAL)


@dataclass
class Offertpost:
    benämning: str
    beskrivning: str
    pris: str


def _poster(sajt: Sajtresultat) -> list[Offertpost]:
    return [
        Offertpost(
            "Manuell granskning",
            "Hela kassaflödet testas med skärmläsare (NVDA) och enbart "
            "tangentbord. Startsida, kategori, produktsida, varukorg och kassa. "
            "Automatiska verktyg hittar ungefär en tredjedel av bristerna — "
            "det här är de återstående två tredjedelarna.",
            f"{kr(PRIS_GRANSKNING)} kr",
        ),
        Offertpost(
            "Rapport och åtgärdslista",
            "Varje brist beskriven på svenska, med skärmbild, WCAG-referens "
            "och kodexempel. Sorterad efter allvarlighetsgrad så att er "
            "utvecklare kan arbeta uppifrån och ner.",
            "Ingår",
        ),
        Offertpost(
            "Underlag till tillgänglighetsredogörelse",
            "Den redogörelse lagen kräver, förberedd för publicering på er "
            "sajt.",
            "Ingår",
        ),
        Offertpost(
            "Genomgång",
            "Fyrtio minuter med er utvecklare eller e-handelsansvarig när "
            "rapporten levererats, så att inget blir hängande.",
            "Ingår",
        ),
        Offertpost(
            "Åtgärdsarbete (valfritt)",
            "Om ni hellre vill att jag lagar felen än att göra det själva. "
            "Debiteras löpande efter faktiskt nedlagd tid, med tak som avtalas "
            "i förväg.",
            f"{kr(TIMPRIS_ATGARD)} kr/tim",
        ),
        Offertpost(
            "Löpande övervakning (valfritt)",
            "Automatisk omskanning varje vecka med larm när en ny release "
            "återinför en brist, samt uppdaterad redogörelse. Sägs upp när "
            "som helst.",
            f"från {kr(PRIS_OVERVAKNING_FRAN)} kr/mån",
        ),
    ]


def offert_html(
    sajt: Sajtresultat,
    *,
    mottagare: str,
    avsändare: str,
    kontakt: str = "",
) -> str:
    """Bygger en fristående offert i HTML."""
    idag = date.today()
    giltig_till = idag + timedelta(days=GILTIGHET_DAGAR)

    rader = "\n".join(
        f"<tr><td><b>{html.escape(p.benämning)}</b><br>"
        f'<span style="color:var(--dämpad);font-size:14px">'
        f"{html.escape(p.beskrivning)}</span></td>"
        f'<td class="num" style="white-space:nowrap;vertical-align:top">'
        f"{html.escape(p.pris)}</td></tr>"
        for p in _poster(sajt)
    )

    # Skanningsresultatet motiverar priset. Utan siffror är offerten bara ett
    # påstående om att något behöver göras.
    if sajt.genomförd:
        underlag = (
            f"Den inledande skanningen av {html.escape(sajt.domän)} hittade "
            f"<b>{sajt.antal_brott} element</b> som bryter mot WCAG 2.1 AA, "
            f"varav <b>{sajt.kritiska}</b> allvarliga eller kritiska. "
            "Den siffran kommer från en automatisk genomgång och är därför "
            "sannolikt i underkant."
        )
    else:
        underlag = (
            "Offerten utgår från ett normalstort e-handelsflöde. Omfattningen "
            "justeras om sajten visar sig vara väsentligt större."
        )

    return f"""<style>{CSS}
.offert-tabell td {{ padding: 14px 10px; vertical-align: top; }}
.summa {{ font-size: 22px; font-weight: 700; }}
.villkor {{ font-size: 14px; color: var(--dämpad); }}
.villkor dt {{ font-weight: 600; color: var(--text); margin-top: 12px; }}
.villkor dd {{ margin: 2px 0 0; }}
</style>
<div class="ark">
  <header>
    <div class="etikett">Offert</div>
    <h1>Tillgänglighetsgranskning av {html.escape(sajt.domän)}</h1>
    <div class="meta">
      Till {html.escape(mottagare)} &middot; {idag.isoformat()} &middot;
      giltig till {giltig_till.isoformat()}
    </div>
  </header>

  <h2>Bakgrund</h2>
  <p class="ingress">{underlag}</p>
  <p>
    Sedan juni 2025 omfattas e-handel av lagen om vissa produkters och
    tjänsters tillgänglighet. Kraven följer EN 301 549, som hänvisar till
    WCAG 2.1 nivå AA. Post- och telestyrelsen utövar tillsyn och kan besluta
    om förelägganden, vite och sanktionsavgifter.
  </p>

  <h2>Vad som ingår</h2>
  <table class="offert-tabell">
    <tbody>{rader}</tbody>
  </table>

  <h2>Pris</h2>
  <p>
    <span class="summa">{kr(PRIS_GRANSKNING)} kr</span>
    <span class="villkor">exklusive moms, fast pris</span>
  </p>
  <p class="villkor">
    Fast pris, inte löpande räkning. Tar granskningen längre tid än beräknat
    är det min risk, inte er.
  </p>

  <h2>Villkor</h2>
  <dl class="villkor">
    <dt>Leveranstid</dt>
    <dd>Rapporten levereras inom tio arbetsdagar från beställning.</dd>
    <dt>Betalning</dt>
    <dd>Faktura vid leverans, trettio dagar netto.</dd>
    <dt>Vad ni behöver bidra med</dt>
    <dd>
      Tillgång till en testmiljö eller möjlighet att lägga en testorder, samt
      en kontaktperson för frågor under arbetet.
    </dd>
    <dt>Vad som inte ingår</dt>
    <dd>
      Åtgärdsarbete, om det inte beställs separat. Granskningen är inte ett
      juridiskt utlåtande och innebär ingen garanti för hur en
      tillsynsmyndighet skulle bedöma sajten. Ingen leverantör kan lova det.
    </dd>
    <dt>Avbeställning</dt>
    <dd>Kostnadsfritt fram till att arbetet påbörjats.</dd>
  </dl>

  <footer>
    {html.escape(avsändare)}{' &middot; ' + html.escape(kontakt) if kontakt else ''}
  </footer>
</div>
"""


def skriv_offert(
    sajt: Sajtresultat,
    sökväg: Path,
    *,
    mottagare: str,
    avsändare: str,
    kontakt: str = "",
) -> Path:
    sökväg.parent.mkdir(parents=True, exist_ok=True)
    sökväg.write_text(
        offert_html(sajt, mottagare=mottagare, avsändare=avsändare, kontakt=kontakt),
        encoding="utf-8",
    )
    return sökväg
