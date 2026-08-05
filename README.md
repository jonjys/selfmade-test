# Tillgänglighetsgranskning för svensk e-handel

Marknadsresearch, skanner och landningssida för en tjänst som granskar
e-handelssajter mot tillgänglighetslagen (EAA / EN 301 549 / WCAG 2.1 AA).

## Vad som finns här

| Katalog | Innehåll |
|---|---|
| [`MARKNADSANALYS.md`](MARKNADSANALYS.md) | Kritisk omprövning av 30 affärsidéer, urval och beslut |
| [`scanner/`](scanner/) | Skanner i Python som hittar brister och genererar rapport |
| [`site/`](site/) | Landningssidan |

## Snabbstart

```bash
# Skanna en sajt
cd scanner
pip install -r requirements.txt
python -m a11yscan.cli --url https://exempel.se --ut resultat/

# Bygg landningssidan
python3 site/build.py
```

Bygget ger två filer:

* **`public/index.html`** — ett fullständigt dokument med teckenkodning och
  viewport. Den är **incheckad i repot** och är det Vercel publicerar. Öppnar
  du filen direkt i telefonen fungerar den också, helt utan uppkoppling.
* `site/artifact.html` — samma innehåll utan skalett, för plattformar som
  tillhandahåller den själva. Checkas inte in.

## Publicering

`vercel.json` pekar ut `public/` som utdatakatalog och stänger av bygg- och
installationsstegen. Sidan är redan byggd och incheckad, så publiceringen kan
inte gå sönder av att byggmiljön saknar Python.

**Kör `python3 site/build.py` och checka in `public/index.html` varje gång du
ändrat `site/index.src.html`** — annars ligger den gamla sidan kvar ute.

Innan första publiceringen: byt `MOTTAGARE` i `site/index.src.html` från
platshållaren. Tills dess vägrar formuläret öppna ett mejlfönster och säger
till besökaren att sidan inte är färdigkonfigurerad.

## Affärsmodellen i en mening

Gratis skanning ger en minirapport med de tre värsta bristerna, minirapporten
säljer en granskning för 19 900 kr, och granskningen säljer en övervakning för
2 900–5 900 kr i månaden.

Med 9–18 prenumeranter når man 50 000 kr i månaden. Det är storleksordningen
som gjorde att den här idén valdes framför en micro-SaaS på 19 dollar, där
samma intäkt kräver 250 kunder.

## Två principer som är inbyggda och testade

**En sajt som inte gick att nå kan aldrig se felfri ut.** Det farligaste
möjliga felet i det här verktyget vore att säga till en kund att allt är i sin
ordning när skanningen aldrig kom fram. Det finns ett test som låser fast det.

**Rapporten skriver ut vad den inte täcker.** Automatiska verktyg fångar
ungefär en tredjedel av bristerna. Att sälja en maskinskanning som
"efterlevnad" är precis det amerikanska FTC bötfällde en widgetleverantör en
miljon dollar för.

## Hela kedjan

| Steg | Vad | Var |
|---|---|---|
| 1 | Skanna 50 sajter | `a11yscan.cli --sajter` |
| 2 | Skicka första mejlet | `utkast/<domän>/1_forsta.eml` |
| 3 | Följ upp dag 4, avsluta dag 10 | `2_uppfoljning.eml`, `3_avslut.eml` |
| 4 | Någon svarar ja → leverera rapporten | `4_leverans.eml` + `rapporter/*.html` |
| 5 | Intresse för granskning → skicka offert | `offerter/*.html` |
| 6 | Genomför granskningen | [`GRANSKNINGSPROTOKOLL.md`](scanner/GRANSKNINGSPROTOKOLL.md) |
| 7 | Fakturera, erbjud övervakning | — |

## Måltavlor

[`scanner/sajter.exempel.txt`](scanner/sajter.exempel.txt) innehåller 39
verifierat nåbara svenska e-handlare, sorterade efter hur nära målgruppen de
ligger. Kopiera till `sajter.txt` och stryk det du inte vill ha.

## Status

Allt som går att bygga utan kunder är byggt. 143 tester gröna, och de flesta
av dem kom till för att en skarp körning mot riktiga svenska sajter avslöjade
något fixturen inte gjorde.

Skannern är körd mot 39 svenska e-handlare. Landningssidan är publicerad och
går igenom sin egen skanner utan anmärkning. Mejlsekvensen, offerten,
redogörelsen och granskningsprotokollet ligger klara.

Ingen kund är kontaktad. Det är hela steg 2 och framåt, och det är den enda
delen som avgör om det här blir pengar.

**Innan första utskicket:** byt `MOTTAGARE` i `site/index.src.html` från
platshållaren och kör `python3 site/build.py`. Tills dess säger formuläret
till besökaren att sidan inte är färdigkonfigurerad, i stället för att öppna
ett mejlfönster till en påhittad adress.
