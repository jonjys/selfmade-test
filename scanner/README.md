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

### Bakom en proxy

I vissa miljöer använder Chromium inte proxyn för sina egna anrop och blir
resatt, medan Pythons nätverksstack kommer fram. **Skannern upptäcker det
själv** och byter hämtväg efter första misslyckandet, och skriver ut att den
gjort det. `--via-python` finns för att tvinga fram det direkt.

Omvägen är långsammare men hittar exakt lika mycket — det finns ett test som
låser fast just det.

## Användning

```bash
# Enskild sajt
python -m a11yscan.cli --url https://exempel.se

# Många sajter, med färdiga mejlutkast
python -m a11yscan.cli --sajter sajter.txt --ut resultat/ \
    --avsandare "Ditt Namn" --avsandaradress "du@dindoman.se"
```

Utdata i `resultat/`:

| Fil | Innehåll |
|---|---|
| `radata.json` | Allt som hittades, per sida och regel |
| `rapporter/*.md` | Minirapport per sajt, att bifoga i mejl |
| `rapporter/*.html` | Full rapport med inbäddade skärmbilder — leveransen |
| `skärmbilder/` | Felande element med röd ram och sammanhang |
| `leadlista.csv` | Sajterna sorterade efter antal allvarliga brister |
| `utkast/<domän>/*.eml` | Hela mejlsekvensen, fyra per sajt |
| `offerter/*.html` | Färdig offert att skicka när någon säger ja |
| `redogorelser/*.md` | Utkast till tillgänglighetsredogörelse per sajt |
| `ringlista.csv` | Arbetslista med öppningsreplik per rad |

## Mejlsekvensen

Anges `--avsandare` skrivs fyra `.eml`-utkast per sajt. De öppnas i vanlig
e-postklient.

| Fil | När | Vad den gör |
|---|---|---|
| `1_forsta.eml` | dag 0 | Leder med en konkret brist på deras sajt |
| `2_uppfoljning.eml` | dag 4 | Kortare, tillför en ny uppgift — inte en påminnelse |
| `3_avslut.eml` | dag 10 | Släpper taget. Ger ofta fler svar än ännu en påminnelse |
| `4_leverans.eml` | vid "ja" | Levererar rapporten och säljer granskningen lågmält |

De tre första är en tidsplan. Det fjärde ligger och väntar tills någon svarar.

**Ingenting skickas automatiskt, och mottagarfältet lämnas tomt.** Ett kallt
utskick till fel person skadar varumärket mer än ett uteblivet mejl, så varje
utkast ska läsas av en människa som fyller i adressen.

Mejlet leder med en konkret observation, inte med ett erbjudande. "Kassan går
inte att slutföra med tangentbord" öppnas; "vi erbjuder tillgänglighetstjänster"
gör det inte. Modulen väljer därför medvetet den mest begripliga bristen som
krok, inte den axe råkar gradera högst.

Varje utkast innehåller en avanmälningsrad och samma avgränsning som rapporten.
Kallt B2B-utskick är tillåtet i Sverige, men mottagaren ska enkelt kunna säga
nej.

## Offerten

Genereras samtidigt som mejlen, en per skannad sajt. Den använder sajtens
faktiska skanningssiffror som motivering — utan dem är offerten bara ett
påstående om att något behöver göras.

Priset är fast, inte löpande räkning. En köpare som inte kan bedöma hur många
timmar som krävs tolkar timpris som obegränsad risk, och fastpris vinner
därför i det här segmentet. Ändra beloppen överst i `a11yscan/offert.py`.

## Tillgänglighetsredogörelsen

Lagen kräver att tjänsten har en redogörelse som beskriver hur tillgänglig den
är, vad som brister och hur man påtalar det. Offerten lovar underlag till den,
och `redogorelser/` innehåller ett utkast per sajt.

Två saker är medvetna: kundens kontaktuppgifter fylls aldrig i på gissning
utan står som hakparenteser, och dokumentet skriver aldrig "helt förenlig" —
en automatisk skanning kan inte belägga det påståendet.

## Den betalda granskningen

[`GRANSKNINGSPROTOKOLL.md`](GRANSKNINGSPROTOKOLL.md) är arbetsordningen för
granskningen à 19 900 kr — de två tredjedelar skannern inte hittar. Följ
ordningen; den är lagd så att de dyraste fynden kommer först ifall tiden tar
slut.

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
4. **Borttagen fokusmarkering.** Kontrollen fokuserar elementen på riktigt och
   jämför den renderade stilen före och efter. Att i stället läsa sidans CSS
   fungerar inte — en webbläsare vägrar läsa regler ur en stilmall på annan
   domän, och nästan alla sajter lägger sin CSS på ett CDN.

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
brister där varje fel är kommenterat med vilken regel det ska utlösa. Fixturen
innehåller också mönster hämtade ordagrant från riktiga svenska sajter där
kontrollerna tidigare larmade fel, så att de inte kan smyga tillbaka.

`.github/workflows/test.yml` kör svitet vid varje push, och kontrollerar
dessutom att `public/index.html` är ombyggd efter ändringar i källfilen — en
gammal publicerad sida syns annars ingenstans förrän en besökare hittar den.

## Kända begränsningar

* Sajter bakom inloggning eller aggressivt bottskydd skannas inte.
* Bara tre sidtyper per sajt. En riktig granskning behöver fler sidmallar.
* Fokuskontrollen fokuserar upp till 40 element per sida. På en sajt med
  hundratals kontroller är det ett stickprov, inte en heltäckning.

## Licens för tredjepartskod

`vendor/axe.min.js` är axe-core 4.10.2 från Deque Systems, licensierad under
Mozilla Public License 2.0. Filen är vendorad i stället för hämtad från CDN så
att en skanning ger samma resultat över tid.
