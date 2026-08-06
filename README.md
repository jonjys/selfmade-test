# Tillgänglighetsgranskning för svensk e-handel

Marknadsresearch, skanner och landningssida för en tjänst som granskar
e-handelssajter mot tillgänglighetslagen (EAA / EN 301 549 / WCAG 2.1 AA).

## Vad som finns här

| Katalog | Innehåll |
|---|---|
| [`MARKNADSANALYS.md`](MARKNADSANALYS.md) | Kritisk omprövning av 30 affärsidéer, urval och beslut |
| [`scanner/`](scanner/) | Skanner i Python som hittar brister och genererar rapport |
| [`web/`](web/) | Webbappen: startsida och kundernas statussidor (Next.js) |
| [`site/`](site/) | Den statiska landningssidan, för publicering som fragment |

## Snabbstart

```bash
# Skanna en sajt
cd scanner
pip install -r requirements.txt
python -m a11yscan.cli --url https://exempel.se --ut resultat/

# Bygg webbappen
cd web && npm install && npm run build
```

## Webbappen

`web/` är en Next.js-app med statisk export. Den innehåller startsidan och en
statussida per kund under `/status/<domän>/`.

Statussidan är det som gör övervakningsprenumerationen värd att behålla. Utan
den märks tjänsten bara när något gått sönder, och en leverantör som hör av
sig enbart med dåliga nyheter upplevs som en kostnad.

Datan kommer från skannern och bakas in vid bygget:

```bash
cd scanner
python -m a11yscan.cli --sajter kunder.txt --ut resultat/ \
    --bevaka bevakning.json --webbdata ../web/data/kunder.json
cd ../web && npm run build
```

Ingen databas och ingen serverfunktion. En prenumerationsprodukt som ska tjäna
pengar utan tillsyn ska ha så få rörliga delar som möjligt — det som inte kan
gå sönder klockan tre på natten behöver ingen jour.

`site/` innehåller den äldre statiska sidan. Den lever kvar för publicering på
plattformar som tillhandahåller egen HTML-skalett.

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
| 8 | Veckoskanning i cron, larm bara vid regression | `--bevaka` |
| 9 | Kunden ser sin status när som helst | `/status/<domän>/` |

## Måltavlor

[`scanner/sajter.exempel.txt`](scanner/sajter.exempel.txt) innehåller 39
verifierat nåbara svenska e-handlare, sorterade efter hur nära målgruppen de
ligger. Kopiera till `sajter.txt` och stryk det du inte vill ha.

## Status

Allt som går att bygga utan kunder är byggt. 154 tester gröna, och de flesta
av dem kom till för att en skarp körning mot riktiga svenska sajter avslöjade
något fixturen inte gjorde.

Skannern är körd mot 39 svenska e-handlare. Webbappen är byggd och går igenom
sin egen skanner utan anmärkning — både startsidan och statussidorna.
Mejlsekvensen, offerten, redogörelsen, granskningsprotokollet och
övervakningsmotorn ligger klara.

Ingen kund är kontaktad. Det är hela steg 2 och framåt, och det är den enda
delen som avgör om det här blir pengar.

**Innan första utskicket:** byt `MOTTAGARE` i `site/index.src.html` från
platshållaren och kör `python3 site/build.py`. Tills dess säger formuläret
till besökaren att sidan inte är färdigkonfigurerad, i stället för att öppna
ett mejlfönster till en påhittad adress.
