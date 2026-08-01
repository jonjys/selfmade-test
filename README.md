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

## Status

Skannern är körd och testad, landningssidan är byggd och går igenom sin egen
skanner utan anmärkning. Ingen kund är kontaktad än — nästa steg är att köra
skannern mot 50 svenska e-handelssajter och skicka minirapporterna.
