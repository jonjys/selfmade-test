# Granskningsprotokoll

Det här är arbetsordningen för den betalda granskningen à 19 900 kr. Skannern
gör grovjobbet; det här är de två tredjedelar den inte hittar.

Räkna med 4–6 timmar för en normal e-handelssajt. Följ ordningen — den är
lagd så att de dyraste fynden kommer först, ifall tiden tar slut.

## Innan du börjar

- [ ] Kör skannern mot sajten. Rådatan är utgångspunkten, inte facit.
- [ ] Installera NVDA (gratis, Windows) eller använd VoiceOver (macOS).
- [ ] Fråga kunden om testmiljö. Går det inte: handla för en liten summa och
      be om kreditering. Lägg **aldrig** en skarp order utan att ha stämt av.
- [ ] Notera vilken plattform sajten kör. Shopify, Woo och Centra har alla
      kända mönster som återkommer.

## 1. Kassaflödet med enbart tangentbord

Det här är det dyraste fyndet och det som säljer övervakningen. Koppla bort
musen helt.

- [ ] Navigera från startsida till slutförd order med enbart Tab, Shift+Tab,
      Enter, Blanksteg och piltangenter.
- [ ] Går det att lägga en vara i varukorgen?
- [ ] Går varianturval (storlek, färg) att använda?
- [ ] Går det att ändra antal och ta bort rader i varukorgen?
- [ ] Går fraktval och betalsätt att välja?
- [ ] Går det att slutföra köpet?
- [ ] Syns fokus hela vägen? Notera varje steg där markeringen försvinner.
- [ ] Fastnar fokus någonstans (modaler, cookiebanner, chattwidget)?

**Skriv ner exakt var det bryter, med skärmbild.** Ett enda "här går det inte
att komma vidare" är värt hela granskningen för kunden.

## 2. Skärmläsare på kritiska sidor

- [ ] Startsida: går det att förstå vad sajten säljer?
- [ ] Produktsida: annonseras pris, lagerstatus och variantval begripligt?
- [ ] Varukorg: läses antal och summa upp korrekt?
- [ ] Kassa: annonseras felmeddelanden när ett fält är fel ifyllt?
- [ ] Bekräftelse: får man veta att ordern gick igenom?

Vanliga fynd: pris som läses som "1 2 9 9", knappar som heter "läs mer" utan
sammanhang, felmeddelanden som aldrig annonseras.

## 3. Cookiebanner och overlays

Nästan alltid trasiga, och de blockerar allt annat.

- [ ] Går bannern att stänga med tangentbord?
- [ ] Fångas fokus i den tills man valt?
- [ ] Går den att nå med skärmläsare innan resten av sidan?

## 4. Formulär

- [ ] Har varje fält en synlig etikett som står kvar när man skriver?
- [ ] Är obligatoriska fält markerade på annat sätt än enbart färg?
- [ ] Beskriver felmeddelanden vad som är fel och hur man rättar det?
- [ ] Flyttas fokus till felet vid misslyckad validering?

## 5. Zoom och förstoring

- [ ] Zooma till 200 %. Försvinner något innehåll?
- [ ] Zooma till 400 %. Går sidan fortfarande att använda?
- [ ] Testa i mobilbredd. Fungerar menyn med tangentbord?

## 6. Kontrast och färg

Skannern täcker det mesta här, men inte allt.

- [ ] Text på bild — skannern missar den nästan alltid.
- [ ] Bärs information någonstans enbart av färg? ("Röda rader är slutsålda.")
- [ ] Syns fokusmarkeringen mot alla bakgrunder den hamnar på?

## 7. Rörelse

- [ ] Finns automatiskt spelande karuseller? Går de att pausa?
- [ ] Respekteras `prefers-reduced-motion`?

## Sammanställning

- [ ] Slå ihop manuella fynd med skannerns rådata.
- [ ] Sortera efter allvarlighetsgrad, inte efter var de hittades.
- [ ] Skriv varje fynd som: vad som händer, för vem, var, hur det rättas.
- [ ] Skärmbild på allt som går att fotografera.
- [ ] Fyll i tillgänglighetsredogörelsen.
- [ ] Boka genomgången innan du skickar rapporten — svarsfrekvensen är högre
      när mötet redan står i kalendern.

## Vad du aldrig skriver i rapporten

- Att sajten "uppfyller" eller "inte uppfyller" lagen. Du beskriver tekniska
  brister mot en standard. Bedömningen är myndighetens.
- Att åtgärderna garanterar godkännande.
- En exakt tidsuppskattning som låter som en offert. Ange storleksordning.
