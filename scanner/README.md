# Tillgänglighetsskanner

Skannar e-handelssajter mot WCAG 2.1 AA och genererar en svensk rapport plus en
lead-lista. Verktyget är steg ett i affärsmodellen: en gratis minirapport är
dörröppnaren till en betald granskning.

## Installation

```bash
pip install -r requirements.txt
python -m playwright install chromium   # hoppa över om Chromium redan finns
```

Finns Chromium förinstallerad hittar skannern den själv via
`PLAYWRIGHT_BROWSERS_PATH`. Peka annars ut binären med `A11YSCAN_CHROMIUM`.

## Användning

```bash
# Enskild sajt
python -m a11yscan.cli --url https://exempel.se

# Många sajter, tre parallellt
python -m a11yscan.cli --sajter sajter.txt --ut resultat/ --samtidighet 3
```

Utdata i `resultat/`:

| Fil | Innehåll |
|---|---|
| `radata.json` | Allt som hittades, per sida och regel |
| `rapporter/*.md` | En minirapport per sajt, avsedd att bifogas i mejl |
| `leadlista.csv` | Alla sajter sorterade efter antal allvarliga brister |

## Vad skannern gör

Per sajt läses startsidan, en produktsida och varukorgen. Produktsidan hittas
genom att leta efter vanliga sökvägsmönster i sidans länkar.

**Vi lägger aldrig en order.** Skanningen går till varukorgen och stannar där.

Reglerna som körs är axe-cores WCAG 2.1 A- och AA-regler, eftersom det är den
nivå EN 301 549 och tillgänglighetslagen hänvisar till. Best-practice-regler
körs medvetet inte — falska positiva är det snabbaste sättet att förlora en
kunds förtroende, och det är precis det klagomål som återkommer i recensionerna
av tillgänglighetsapparna i Shopifys appbutik.

### Egna kontroller utöver axe-core

Fyra kontroller är egna, och de är den del som faktiskt skiljer verktyget från
en gratis Lighthouse-körning:

1. **Klickbara element som inte går att nå med tangentbord** — `div` och `span`
   med klickhanterare. Sitter det i kassan kan kunden inte handla.
2. **Saknad genväg till huvudinnehållet.**
3. **Fält som bara har platshållartext.** axe-core godkänner det här, eftersom
   `placeholder` räknas som tillgängligt namn enligt accname-specen. Problemet
   är verkligt ändå: texten försvinner när kunden börjar skriva.
4. **Borttagen fokusmarkering** — `outline: none` utan synlig ersättning.

## Ärlighet i rapporten

Två saker är inbyggda med avsikt:

* Rapporten skriver ut att automatisk skanning fångar ungefär en tredjedel av
  bristerna, och uppskattar det verkliga antalet. Att sälja en skanning som
  "efterlevnad" är exakt det [FTC bötfällde accessiBe 1 MUSD
  för](https://ratedwithai.com/blog/accessibe-review-2026).
* En sajt som inte gick att nå kan aldrig se felfri ut. Det testas explicit i
  `test_onåbar_sajt_ser_aldrig_felfri_ut`.

## Tester

```bash
python -m pytest tests/ -v
```

Testerna kör mot `tests/fixtures/trasig_butik.html`, en sida med avsiktliga
brister där varje fel är kommenterat med vilken regel det ska utlösa.

## Kända begränsningar

* Sajter bakom inloggning eller aggressivt bottskydd skannas inte.
* Bara tre sidtyper per sajt. En riktig granskning behöver fler sidmallar.
* Skärmbilder på felande element är inte implementerat än. Det är nästa steg —
  en bild på den trasiga knappen säljer bättre än en HTML-snutt.

## Licens för tredjepartskod

`vendor/axe.min.js` är axe-core 4.10.2 från Deque Systems, licensierad under
Mozilla Public License 2.0. Filen är vendorad i stället för hämtad från CDN så
att en skanning ger samma resultat över tid.
