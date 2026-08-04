"""Skanningsmotor: kör axe-core plus egna tangentbordskontroller mot en sajt.

Designbeslut värda att känna till:

* axe-core körs från en vendorad fil i repot, inte från CDN. Skanningar ska ge
  samma resultat i dag och om sex månader.
* Endast reglerna bakom WCAG 2.1 A/AA körs, eftersom det är den nivå
  EN 301 549 hänvisar till. Att rapportera AAA-brister skulle ge falsk oro.
* Vi lägger till tre egna kontroller som axe inte täcker. De handlar alla om
  tangentbord, vilket är den vanligaste orsaken till att en kassa blir omöjlig
  att slutföra — och det som säljer en granskning.
* Vi lägger aldrig en order. Skanningen går till varukorgen och stannar där.
"""

from __future__ import annotations

import asyncio
import glob
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, Page, Error as PWError

from .rules import IMPACT_ORDER

log = logging.getLogger(__name__)

AXE_PATH = Path(__file__).resolve().parent.parent / "vendor" / "axe.min.js"

# EN 301 549 hänvisar till WCAG 2.1 nivå A och AA. Inget annat.
AXE_TAGGAR = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]

# Chromiums bakgrundstrafik (komponentuppdateringar, varianter, säker
# webbläsning) går i klartext till Googles servrar. Bakom en proxy som bara
# tillåter CONNECT avvisas de, och felen är svåra att skilja från riktiga
# anslutningsproblem hos sajten vi skannar. De tillför heller ingenting vid en
# skanning, så vi stänger av dem.
CHROMIUM_ARGUMENT = (
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-domain-reliability",
    "--disable-sync",
    "--disable-client-side-phishing-detection",
    "--safebrowsing-disable-auto-update",
    "--metrics-recording-only",
    "--no-first-run",
    "--no-default-browser-check",
)

# Marginal i pixlar runt ett felande element vid skärmbild.
SKÄRMBILD_MARGINAL = 60

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36 (tillganglighetsskanner; kontakt i README)"
)

# Vanliga svenska och engelska sökvägar för de sidtyper vi vill åt.
PRODUKT_MÖNSTER = ("/products/", "/produkt/", "/produkter/", "/vara/", "/p/")
VARUKORG_SÖKVÄGAR = ("/cart", "/varukorg", "/kundvagn", "/kassa", "/checkout")


@dataclass
class Överträdelse:
    """En enskild brist, normaliserad oavsett om den kommer från axe eller oss."""

    regel_id: str
    impact: str
    antal: int
    sidtyp: str
    url: str
    beskrivning: str
    exempel_selektor: str = ""
    exempel_html: str = ""
    skärmbild: str = ""


@dataclass
class Sidresultat:
    url: str
    sidtyp: str
    överträdelser: list[Överträdelse] = field(default_factory=list)
    fel: str = ""


@dataclass
class Sajtresultat:
    domän: str
    startadress: str
    sidor: list[Sidresultat] = field(default_factory=list)
    fel: str = ""

    @property
    def alla_överträdelser(self) -> list[Överträdelse]:
        return [ö for sida in self.sidor for ö in sida.överträdelser]

    @property
    def lyckade_sidor(self) -> list[Sidresultat]:
        return [s for s in self.sidor if not s.fel]

    @property
    def genomförd(self) -> bool:
        """Sant först när minst en sida faktiskt gick att skanna.

        Utan den här kontrollen ser en sajt som vägrar anslutning ut som en
        sajt utan brister, vilket är det värsta möjliga felet i det här
        verktyget — vi skulle berätta för en kund att allt är i sin ordning.
        """
        return not self.fel and bool(self.lyckade_sidor)

    @property
    def antal_brott(self) -> int:
        """Totalt antal element med brister, inte antal regeltyper."""
        return sum(ö.antal for ö in self.alla_överträdelser)

    @property
    def kritiska(self) -> int:
        return sum(
            ö.antal for ö in self.alla_överträdelser if ö.impact in ("critical", "serious")
        )

    def värsta(self, n: int = 3) -> list[Överträdelse]:
        """De brister som ska ligga överst i säljbrevet."""
        return sorted(
            self.alla_överträdelser,
            key=lambda ö: (IMPACT_ORDER.get(ö.impact, 9), -ö.antal),
        )[:n]


# JavaScript för de tre egna kontrollerna. Körs i sidans kontext.
EGNA_KONTROLLER_JS = """
() => {
  const resultat = [];

  // 1. Klickbara element som inte går att nå med tangentbord.
  //    Vi letar efter div/span med klickhanterare eller pekarmarkör som
  //    varken har tabindex, roll eller är naturligt fokuserbara.
  const naturligtFokuserbar = 'a[href], button, input, select, textarea, [tabindex]';
  const misstänkta = [];
  document.querySelectorAll('div, span, li').forEach((el) => {
    if (el.matches(naturligtFokuserbar)) return;
    if (el.closest(naturligtFokuserbar)) return;
    // Ett omslag som innehåller något fokuserbart är åtkomligt via innehållet
    // och är inte en falsk knapp. Utan den här raden flaggas sidans yttersta
    // div — den som innehåller hela sajten — som en oåtkomlig knapp, och en
    // enda sådan rad i rapporten gör hela dokumentet otrovärdigt.
    if (el.querySelector(naturligtFokuserbar)) return;
    // Explicit dolt för hjälpmedel. Ett element som är borttaget ur
    // tillgänglighetsträdet kan man inte kräva tangentbordsåtkomst av — det
    // är typiskt ett menyöverlägg som stänger vid klick, med en riktig
    // stängknapp någon annanstans.
    if (el.closest('[aria-hidden="true"]')) return;
    // En etikett som omsluter en formulärkontroll är åtkomlig via kontrollen.
    // Utan det här undantaget flaggas varje snyggt byggd vippa och radioknapp,
    // och en rapport full av falska positiva slutar man läsa.
    const etikett = el.closest('label');
    if (etikett && etikett.querySelector('input, select, textarea')) return;

    const stil = window.getComputedStyle(el);

    // Går inte att klicka på ens med mus. Vanligt på overlays som ligger kvar
    // i DOM:en men är avstängda.
    if (stil.pointerEvents === 'none') return;
    // Osynligt eller utan yta. Skärmläsartext och nollstora omslag är inga
    // knappar även om de råkar ärva en pekare.
    const ruta = el.getBoundingClientRect();
    if (ruta.width < 8 || ruta.height < 8) return;
    if (stil.visibility === 'hidden' || stil.display === 'none') return;

    const roll = el.getAttribute('role');
    if (roll === 'button' || roll === 'link') {
      // Har roll men ingen tabindex — annonseras som knapp men går inte att nå.
      if (!el.hasAttribute('tabindex')) misstänkta.push(el);
      return;
    }

    // En inline-hanterare är ett otvetydigt tecken.
    if (typeof el.onclick === 'function') { misstänkta.push(el); return; }

    // cursor: pointer ärvs nedåt. Utan den här kontrollen flaggas varje
    // textnod inuti ett klickbart kort, och vi rapporterar tjugo barn i
    // stället för den enda förälder som faktiskt är problemet. Vi kräver
    // därför att pekaren börjar på det här elementet.
    if (stil.cursor !== 'pointer') return;
    const förälder = el.parentElement;
    if (förälder && window.getComputedStyle(förälder).cursor === 'pointer') return;
    if (!el.textContent.trim()) return;
    misstänkta.push(el);
  });
  if (misstänkta.length) {
    const f = misstänkta[0];
    resultat.push({
      regel_id: 'custom-click-handler-not-focusable',
      impact: 'serious',
      antal: misstänkta.length,
      exempel_html: f.outerHTML.slice(0, 300),
      exempel_selektor: f.tagName.toLowerCase() +
        (f.className && typeof f.className === 'string'
          ? '.' + f.className.trim().split(/\\s+/).slice(0, 2).join('.')
          : ''),
    });
  }

  // 2. Saknad genväg till huvudinnehållet.
  const genvägar = Array.from(document.querySelectorAll('a[href^="#"]')).filter((a) => {
    const t = (a.textContent || '').toLowerCase();
    return t.includes('skip') || t.includes('hoppa') || t.includes('till innehåll');
  });
  if (genvägar.length === 0) {
    resultat.push({
      regel_id: 'custom-no-skip-link',
      impact: 'moderate',
      antal: 1,
      exempel_html: '',
      exempel_selektor: 'body',
    });
  }

  // 3. Fält som bara har platshållartext.
  //    axe-core flaggar inte det här, eftersom placeholder räknas som
  //    tillgängligt namn enligt accname-specen. Problemet är verkligt ändå:
  //    texten försvinner när fältet fylls i.
  const utanEtikett = [];
  document.querySelectorAll('input, textarea').forEach((el) => {
    const typ = (el.getAttribute('type') || 'text').toLowerCase();
    if (['hidden', 'submit', 'button', 'image', 'reset'].includes(typ)) return;
    if (!el.getAttribute('placeholder')) return;
    if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) return;
    if (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`)) return;
    if (el.closest('label')) return;
    utanEtikett.push(el);
  });
  if (utanEtikett.length) {
    const f = utanEtikett[0];
    resultat.push({
      regel_id: 'custom-placeholder-som-etikett',
      impact: 'serious',
      antal: utanEtikett.length,
      exempel_html: f.outerHTML.slice(0, 300),
      exempel_selektor: f.tagName.toLowerCase() +
        (f.name ? `[name="${f.name}"]` : ''),
    });
  }

  // 4. Borttagen fokusmarkering. Vi letar efter CSS-regler som nollar outline
  //    utan att ersätta den med något synligt.
  let nollar = 0;
  let synliga = 0;
  for (const ark of Array.from(document.styleSheets)) {
    let regler;
    try {
      regler = ark.cssRules;
    } catch (e) {
      continue; // Korsdomänark går inte att läsa. Hoppa över.
    }
    if (!regler) continue;
    for (const regel of Array.from(regler)) {
      if (!regel.selectorText || !regel.style) continue;
      if (!regel.selectorText.includes(':focus')) continue;
      const o = regel.style.outline || regel.style.outlineStyle || regel.style.outlineWidth;
      const nollad = o === 'none' || o === '0' || o === '0px';
      const harErsättning =
        regel.style.boxShadow || regel.style.border || regel.style.backgroundColor;
      if (nollad && !harErsättning) {
        nollar += 1;
      } else if (o || regel.style.boxShadow) {
        // Regeln ger tvärtom fokus ett synligt utseende.
        synliga += 1;
      }
    }
  }
  // Bara en sajt som nollar fokus UTAN att någonstans ge det ett synligt
  // utseende har ett verkligt problem. En enskild nollande regel kan vara
  // avsiktlig och kompenseras på annat håll.
  if (nollar > 0 && synliga === 0) {
    resultat.push({
      regel_id: 'custom-no-visible-focus',
      impact: 'serious',
      antal: nollar,
      exempel_html: '',
      exempel_selektor: ':focus',
    });
  }

  return resultat;
}
"""


class Skanner:
    """Skannar sajter. Återanvänder en webbläsarinstans mellan sajter."""

    def __init__(
        self,
        *,
        samtidighet: int = 3,
        timeout_ms: int = 30_000,
        skärmbildskatalog: Path | None = None,
        hämta_via_python: bool = False,
    ) -> None:
        self.samtidighet = samtidighet
        self.timeout_ms = timeout_ms
        self.skärmbildskatalog = skärmbildskatalog
        self.hämta_via_python = hämta_via_python
        self._axe_js = AXE_PATH.read_text(encoding="utf-8")

    async def skanna_många(self, adresser: list[str]) -> list[Sajtresultat]:
        async with async_playwright() as pw:
            startargument: dict = {"args": list(CHROMIUM_ARGUMENT)}
            if binär := hitta_webbläsare():
                log.debug("Använder förinstallerad Chromium: %s", binär)
                startargument["executable_path"] = binär
            if proxy := hitta_proxy():
                log.debug("Använder proxy: %s", proxy["server"])
                startargument["proxy"] = proxy
            webbläsare = await pw.chromium.launch(**startargument)
            grind = asyncio.Semaphore(self.samtidighet)

            async def kör(adress: str) -> Sajtresultat:
                async with grind:
                    return await self._skanna_sajt(webbläsare, adress)

            try:
                resultat = await asyncio.gather(
                    *(kör(a) for a in adresser), return_exceptions=True
                )
            finally:
                await webbläsare.close()

        färdiga: list[Sajtresultat] = []
        for adress, r in zip(adresser, resultat):
            if isinstance(r, BaseException):
                log.warning("Skanning misslyckades för %s: %s", adress, r)
                färdiga.append(
                    Sajtresultat(domän=_domän(adress), startadress=adress, fel=str(r))
                )
            else:
                färdiga.append(r)
        return färdiga

    async def _skanna_sajt(self, webbläsare: Browser, startadress: str) -> Sajtresultat:
        domän = _domän(startadress)
        sajt = Sajtresultat(domän=domän, startadress=startadress)
        kontext = await webbläsare.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1366, "height": 900},
            locale="sv-SE",
        )
        try:
            if self.hämta_via_python:
                await _koppla_python_hämtning(kontext)
            sida = await kontext.new_page()
            sida.set_default_timeout(self.timeout_ms)

            # Startsidan skannas alltid, och används för att hitta de andra.
            start = await self._skanna_sida(sida, startadress, "Startsida")
            sajt.sidor.append(start)

            if start.fel:
                # Går inte startsidan att nå är hela skanningen värdelös.
                sajt.fel = f"Startsidan kunde inte läsas in: {start.fel.splitlines()[0]}"
            else:
                for url, sidtyp in await self._hitta_undersidor(sida, startadress):
                    sajt.sidor.append(await self._skanna_sida(sida, url, sidtyp))
        except Exception as exc:  # noqa: BLE001 — en trasig sajt får inte stoppa körningen
            sajt.fel = str(exc)
        finally:
            await kontext.close()
        return sajt

    async def _injicera_axe(self, sida: Page) -> None:
        """Lägger in axe-core på sidan, även bakom en strikt CSP.

        add_script_tag skapar ett riktigt <script>-element, vilket en sajt med
        Content-Security-Policy utan 'unsafe-inline' vägrar köra. Att utvärdera
        källan direkt går däremot genom felsökningsprotokollet och berörs inte
        av sidans CSP.

        Vi provar taggen först eftersom den är billigare, och faller tillbaka
        bara när CSP:n säger nej. Allt fler sajter sätter CSP, så utan det här
        tappar vi just de kunder som bryr sig mest om sin säkerhet.
        """
        try:
            await sida.add_script_tag(content=self._axe_js)
        except PWError as fel:
            if "Refused to execute" not in str(fel) and "Content Security" not in str(fel):
                raise
            log.debug("CSP blockerade skripttaggen på %s, utvärderar direkt", sida.url)
            await sida.evaluate(self._axe_js)

    async def _fånga_skärmbilder(self, sida: Page, resultat: Sidresultat) -> None:
        """Fotograferar de värsta felande elementen, med röd ram runt.

        Det här är säljmaterialet. En bild på knappen som inte går att nå med
        tangentbord gör mer intryck än en HTML-snutt, särskilt på en mottagare
        som inte läser kod.

        Misslyckas en enskild bild spelar det ingen roll — elementet kan ha
        försvunnit vid en omritning. Vi hoppar över den och går vidare.
        """
        katalog = self.skärmbildskatalog
        assert katalog is not None
        katalog.mkdir(parents=True, exist_ok=True)

        värsta = sorted(
            (ö for ö in resultat.överträdelser if ö.exempel_selektor),
            key=lambda ö: IMPACT_ORDER.get(ö.impact, 9),
        )[:3]

        for ö in värsta:
            try:
                element = sida.locator(ö.exempel_selektor).first
                if not await element.is_visible(timeout=2_000):
                    continue
                # Markera elementet så att mottagaren ser vad som avses.
                await element.evaluate(
                    "el => { el.style.outline = '3px solid #d92d20';"
                    " el.style.outlineOffset = '2px'; }"
                )
                await element.scroll_into_view_if_needed(timeout=2_000)
                namn = f"{_säkert_filnamn(ö.url)}_{ö.regel_id}.png"
                sökväg = katalog / namn

                # Fota med marginal runt elementet. En närbild på en 20 pixlar
                # bred ikon säger ingenting — mottagaren måste se var på sidan
                # felet sitter för att känna igen det.
                ruta = await element.bounding_box()
                if ruta:
                    vy = sida.viewport_size or {"width": 1366, "height": 900}
                    marginal = SKÄRMBILD_MARGINAL
                    klipp = {
                        "x": max(0, ruta["x"] - marginal),
                        "y": max(0, ruta["y"] - marginal),
                        "width": min(ruta["width"] + marginal * 2, vy["width"]),
                        "height": min(ruta["height"] + marginal * 2, vy["height"]),
                    }
                    await sida.screenshot(path=str(sökväg), clip=klipp, timeout=5_000)
                else:
                    await element.screenshot(path=str(sökväg), timeout=5_000)
                ö.skärmbild = namn
                await element.evaluate("el => { el.style.outline = ''; }")
            except Exception as exc:  # noqa: BLE001 — en bild är aldrig kritisk
                log.debug("Kunde inte fota %s: %s", ö.regel_id, exc)

    async def _hitta_undersidor(self, sida: Page, bas: str) -> list[tuple[str, str]]:
        """Letar upp en produktsida och en varukorg. Bäst ansträngning."""
        hittade: list[tuple[str, str]] = []
        try:
            länkar = await sida.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.getAttribute('href'))"
            )
        except PWError:
            return hittade

        produkt = next(
            (
                urljoin(bas, h)
                for h in länkar
                if h and any(m in h.lower() for m in PRODUKT_MÖNSTER)
            ),
            None,
        )
        if produkt:
            hittade.append((produkt, "Produktsida"))

        # Varukorgen ligger nästan alltid på en förutsägbar sökväg.
        for sökväg in VARUKORG_SÖKVÄGAR:
            träff = next(
                (urljoin(bas, h) for h in länkar if h and h.lower().rstrip("/").endswith(sökväg)),
                None,
            )
            if träff:
                hittade.append((träff, "Varukorg"))
                break
        else:
            hittade.append((urljoin(bas, "/cart"), "Varukorg"))

        return hittade

    async def _skanna_sida(self, sida: Page, url: str, sidtyp: str) -> Sidresultat:
        resultat = Sidresultat(url=url, sidtyp=sidtyp)
        try:
            svar = await sida.goto(url, wait_until="domcontentloaded")
            if svar and svar.status >= 400:
                resultat.fel = f"HTTP {svar.status}"
                return resultat

            # Ge lazy-laddat innehåll en chans, men vänta inte på annonsspårare.
            try:
                await sida.wait_for_load_state("networkidle", timeout=6_000)
            except PWError:
                pass

            await _rulla_igenom(sida)

            try:
                await self._injicera_axe(sida)
            except PWError as fel:
                # Sajter som gör en klientomdirigering strax efter inladdning
                # river dokumentet under fötterna på oss. Vänta in det nya
                # dokumentet och försök en gång till innan vi ger upp.
                if "Execution context was destroyed" not in str(fel):
                    raise
                log.debug("Omdirigering under injektion av %s, försöker igen", url)
                await sida.wait_for_load_state("domcontentloaded")
                resultat.url = sida.url
                await self._injicera_axe(sida)
            axe_resultat = await sida.evaluate(
                """async (taggar) => {
                    const r = await window.axe.run(document, {
                        runOnly: { type: 'tag', values: taggar },
                        resultTypes: ['violations'],
                    });
                    return r.violations.map(v => {
                        const n = v.nodes[0];
                        return {
                            regel_id: v.id,
                            impact: v.impact || 'moderate',
                            antal: v.nodes.length,
                            beskrivning: v.description,
                            exempel_selektor: n && n.target ? String(n.target[0]) : '',
                            exempel_html: n && n.html ? n.html.slice(0, 300) : '',
                        };
                    });
                }""",
                AXE_TAGGAR,
            )
            resultat.överträdelser.extend(
                Överträdelse(
                    regel_id=v["regel_id"],
                    impact=v["impact"],
                    antal=v["antal"],
                    sidtyp=sidtyp,
                    url=url,
                    beskrivning=v["beskrivning"],
                    exempel_selektor=v.get("exempel_selektor", ""),
                    exempel_html=v.get("exempel_html", ""),
                )
                for v in axe_resultat
            )

            egna = await sida.evaluate(EGNA_KONTROLLER_JS)
            resultat.överträdelser.extend(
                Överträdelse(
                    regel_id=v["regel_id"],
                    impact=v["impact"],
                    antal=v["antal"],
                    sidtyp=sidtyp,
                    url=url,
                    beskrivning="",
                    exempel_selektor=v.get("exempel_selektor", ""),
                    exempel_html=v.get("exempel_html", ""),
                )
                for v in egna
            )

            if self.skärmbildskatalog:
                await self._fånga_skärmbilder(sida, resultat)
        except Exception as exc:  # noqa: BLE001
            resultat.fel = str(exc)
        return resultat


async def _rulla_igenom(sida: Page) -> None:
    """Rullar sidan till botten så att lazy-laddat innehåll hinner in.

    Utan det här skannas bara det som syns direkt, och allt under vikningen
    ligger kvar som tomma platshållare. På en sajt med lazy-laddade
    produktbilder rapporterades 42 bilder utan alternativtext som i själva
    verket var oladdade platshållare — en siffra som är både för hög och
    omöjlig för kunden att känna igen när de tittar på sin egen sajt.

    Vi rullar tillbaka till toppen efteråt, eftersom skärmbilderna annars
    hamnar fel.
    """
    try:
        await sida.evaluate(
            """async () => {
                const steg = window.innerHeight * 0.8;
                const höjd = () => document.body ? document.body.scrollHeight : 0;
                for (let y = 0; y < Math.min(höjd(), 20000); y += steg) {
                    window.scrollTo(0, y);
                    await new Promise(r => setTimeout(r, 120));
                }
                window.scrollTo(0, 0);
                await new Promise(r => setTimeout(r, 250));
            }"""
        )
    except PWError as fel:
        log.debug("Kunde inte rulla igenom %s: %s", sida.url, fel)


async def _koppla_python_hämtning(kontext) -> None:
    """Låter Python hämta allt webbläsaren begär.

    I miljöer där utgående trafik måste gå genom en proxy använder Chromium
    ibland inte proxyn för sina egna anrop och blir resatt, medan Pythons
    nätverksstack kommer fram utan problem. I stället för att stänga av
    säkerhetskontroller eller kringgå proxyn skickar vi webbläsarens
    förfrågningar genom samma väg som fungerar.

    Kostnaden är att varje anrop tar en omväg och att HTTP/2 tappas. För en
    skanning spelar det ingen roll — sidan renderas likadant.
    """

    def hämta(url: str, metod: str, huvuden: dict[str, str], kropp: bytes | None):
        begäran = urllib.request.Request(url, data=kropp, method=metod)
        for namn, värde in huvuden.items():
            if namn.lower() in ("host", "connection", "content-length"):
                continue
            begäran.add_header(namn, värde)
        # Be alltid om okomprimerat svar. Då slipper vi hantera gzip-avkodning
        # och riskerar inte att skicka en kropp som inte matchar sina huvuden.
        begäran.add_header("Accept-Encoding", "identity")

        with urllib.request.urlopen(begäran, timeout=25) as svar:
            data = svar.read()
            svarshuvuden = {
                k: v
                for k, v in svar.headers.items()
                if k.lower() not in ("content-encoding", "content-length",
                                     "transfer-encoding", "connection")
            }
            return svar.status, svarshuvuden, data

    async def hanterare(route, begäran):
        if not begäran.url.startswith(("http://", "https://")):
            await route.continue_()
            return
        try:
            kropp = begäran.post_data_buffer
            status, huvuden, data = await asyncio.to_thread(
                hämta, begäran.url, begäran.method, begäran.headers, kropp
            )
            await route.fulfill(status=status, headers=huvuden, body=data)
        except urllib.error.HTTPError as fel:
            # Ett 404 är ett giltigt svar och ska nå webbläsaren, inte avbrytas.
            try:
                await route.fulfill(
                    status=fel.code,
                    headers={k: v for k, v in fel.headers.items()
                             if k.lower() not in ("content-encoding", "content-length",
                                                  "transfer-encoding", "connection")},
                    body=fel.read(),
                )
            except Exception:  # noqa: BLE001
                await route.abort()
        except Exception as exc:  # noqa: BLE001
            log.debug("Kunde inte hämta %s: %s", begäran.url, exc)
            await route.abort()

    await kontext.route("**/*", hanterare)


def _domän(adress: str) -> str:
    return urlparse(adress).netloc.replace("www.", "")


def _säkert_filnamn(text: str) -> str:
    """Gör en URL användbar som filnamn utan att tappa igenkänning."""
    rensad = "".join(c if c.isalnum() else "_" for c in text)
    return rensad.strip("_")[-60:] or "sida"


def hitta_webbläsare() -> str | None:
    """Letar upp en förinstallerad Chromium.

    Playwright-paketet från pip förväntar sig en exakt buildversion och vägrar
    starta om katalognamnet inte stämmer, även när en fullt duglig Chromium
    finns på disk. I körmiljöer med förinstallerade webbläsare är det vanligt
    att versionerna glider isär. Vi pekar då ut binären själva i stället för
    att ladda ned en ny.

    Returnerar None när inget hittas, vilket låter Playwright använda sin egen
    upplösning och ge sitt normala felmeddelande.
    """
    if uttrycklig := os.environ.get("A11YSCAN_CHROMIUM"):
        return uttrycklig if Path(uttrycklig).exists() else None

    rot = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    # Full Chromium först — headless shell saknar en del som vissa sajter kräver.
    for mönster in ("chromium-*/chrome-linux/chrome",
                    "chromium_headless_shell-*/chrome-linux/headless_shell"):
        träffar = sorted(glob.glob(str(Path(rot) / mönster)), reverse=True)
        if träffar:
            return träffar[0]
    return None


def hitta_proxy() -> dict[str, str] | None:
    """Läser proxyinställning ur miljön i det format Playwright vill ha.

    Chromium ärver inte HTTPS_PROXY automatiskt. I miljöer där all utgående
    trafik går genom en proxy misslyckas annars varje anrop med
    ERR_CONNECTION_RESET, vilket är svårt att skilja från en sajt som är nere.
    """
    adress = (
        os.environ.get("HTTPS_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("http_proxy")
    )
    if not adress:
        return None
    proxy = {"server": adress}
    if undantag := os.environ.get("NO_PROXY") or os.environ.get("no_proxy"):
        proxy["bypass"] = undantag
    return proxy


def spara_json(resultat: list[Sajtresultat], sökväg: Path) -> None:
    sökväg.parent.mkdir(parents=True, exist_ok=True)
    sökväg.write_text(
        json.dumps([asdict(r) for r in resultat], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
