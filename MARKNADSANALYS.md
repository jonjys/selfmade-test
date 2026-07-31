# Från research till beslut — kritisk omprövning och urval

**Datum:** 2026-07-31
**Mål:** En AI-produkt som realistiskt ger 5 000–50 000 SEK/mån i återkommande intäkter, byggbar av ett mycket litet team, med uppsida.

---

## Del 0: Sammanfattning för den otåliga

1. **Den tidigare topp 10-listan är till största delen ogiltig.** Åtta av tio idéer har redan direkta konkurrenter som säljer exakt det föreslagna erbjudandet till exakt det föreslagna priset. Det var inte "medelhög konkurrens" — det var en mättad marknad.
2. **Orsaken är strukturell.** Allt som en ensam utvecklare kan bygga på en helg med en LLM har redan byggts av hundra andra. "Luckan" i alla dessa idéer var inte en lucka, den var bara osynlig i en Google-sökning på svenska.
3. **Målsättningen på 5 000–50 000 SEK/mån pekar åt motsatt håll mot micro-SaaS.** 50 000 SEK/mån är antingen ~250 kunder à 19 USD eller ~12 kunder à 4 000 SEK. Det andra alternativet är dramatiskt mycket lättare utan distribution.
4. **Rekommendationen är efterlevnad av tillgänglighetslagen/EAA för nordisk e-handel** — granskning, AI-genererade kodfixar och löpande regressionsövervakning. Det är den enda kandidaten där en myndighet just nu aktivt driver efterfrågan, där det billiga alternativet är juridiskt giftigt, och där betalningsviljan redan är bevisad i kronor.

---

## Del 1: Brutal omprövning av den tidigare topp 10-listan

Metod: jag sökte efter faktiskt existerande produkter i varje nisch, på det pris som föreslogs som "luckan". Resultat nedan.

| # | Tidigare idé | Verkligheten 2026 | Dom |
|---|---|---|---|
| 1 | Offert-AI för hantverkare | **Smidia**, **Bliqat** ("AI-offerter för hantverkare på under en minut", med ROT), **ByggLog**, **Construction+**, plus Bygglet och Sigma Kalkyl. Svensk marknad, svenskt språk, ROT inbyggt. | **Död** |
| 2 | LinkedIn-karusellgenerator | Supergrow (19 USD), ContentIn, Postiv, Carosello, Taplio, Connectsafely, m.fl. Minst 14 testade verktyg i publicerade jämförelser, priser 12–29 USD. | **Död** |
| 3 | Churn-recovery-widget | **MRRSaver 29 USD/mån** gör precis det föreslagna. Plus ProsperStack, Upzelo, Recurflux, Churn Buster. Churnkey har lämnat segmentet uppåt. | **Död** |
| 4 | PDF-dataextraktion för bokförare | **Fortnox har lanserat egen AI-tolkning av leverantörsfakturor**, och konkurrerar dessutom nu direkt med byråerna via BLINK. Att bygga ovanpå plattformen som äter ens kunder är en dålig position. | **Död** |
| 5 | Lokal SEO- & recensionssvarare | **Reply Champion 10 USD/mån**, RepliFast från 15 USD, RightResponse 10 USD + 0,20 USD/svar. Priskriget är redan under det föreslagna priset. | **Död** |
| 6 | CV-anonymisering för rekryterare | **TalentVeil**, **CVFormatter**, **RemakeCV**, **Giig**, **HubbaDO** — alla gör anonymisering + byråns mall + 30 sekunder. Flera är gratis. | **Död** |
| 7 | Internlänkning via embeddings | **LinkBoss** gör semantisk analys sedan länge, **Rank Math AI Link Genius** är buntat med en plugin miljontals sajter redan har. Argumentet "de använder gammal nyckelordsmatchning" stämmer inte längre. | **Död** |
| 8 | Avtalsgranskare för frilansare | **Clausely 12,99 USD/mån**, **BeforeYouSign 2,99–9,99 USD per avtal**, ContractClarifyAI 29 USD. Priset som föreslogs (15 USD) ligger *över* marknaden. | **Död** |
| 9 | Felanmälan för fastighet | 25+ svenska fastighetssystem med felanmälan inbyggd; TenFAST m.fl. prissatta från ~825 kr/mån för 3 användare. Man säljer en modul mot system kunden redan betalar för. | **Svag** |
| 10 | Support-QA för e-handel | Zendesk QA (ex-Klaus, uppköpt av Zendesk), MaestroQA, EvaluAgent, Lorikeet, eesel. Enterprise-prissatt, men segmentet är bemannat. | **Svag** |

**Slutsats:** noll av tio kvalificerar sig. Att fortsätta bygga någon av dessa vore att gå in i ett priskrig mot etablerade aktörer utan distribution, produkt eller varumärke.

### Varför gick det så här?

Ett citat ur marknadsanalyserna för 2026 sammanfattar det: *"Vertikal-SaaS-playbooken 'AI för X-bransch' får tolv välfinansierade nykomlingar per kvartal och hundra indie hackers i veckan."* Uppskattningsvis 90 % av AI-wrapper-startups väntas läggas ned under 2026 och 60–70 % genererar noll intäkter.

Det som fortfarande fungerar, enligt samma källor: **nischer med hög regulatorisk komplexitet, nischer med inbäddade mänskliga arbetsflöden, och nischer där domäntillit väger tyngre än produkten.** Det är filtret för resten av det här dokumentet.

---

## Del 2: Omräkning av målet — vilket ändrar allt

| Prispunkt | Kunder för 5 000 kr/mån | för 20 000 kr/mån | för 50 000 kr/mån |
|---|---|---|---|
| 19 USD/mån (~200 kr) | 25 | 100 | **250** |
| 49 USD/mån (~520 kr) | 10 | 39 | **97** |
| 2 900 kr/mån | 2 | 7 | **18** |
| 5 900 kr/mån | 1 | 4 | **9** |
| 12 000 kr/mån | 1 | 2 | **5** |

Att skaffa 250 betalande konsumentkunder utan distribution tar år, och churn på 5–8 %/mån äter upp tillväxten. Att skaffa 9–18 företagskunder är en fråga om ungefär 300–600 kalla kontakter och 30–50 möten. Det är ett arbete som går att göra på egen hand vid sidan av bygget.

**Därför gäller följande urvalskriterier härefter:**

1. ACV över 2 500 kr/mån, annars diskvalificerad.
2. Ett regelverk, en deadline eller ett inbäddat arbetsflöde som skapar efterfrågan — inte "det vore smidigt".
3. Köparen ska gå att identifiera med namn och adress från en publik källa.
4. Det ska kosta mer än en helg att kopiera — domänkunskap, data eller tillit ska ingå.
5. Återkommande av naturliga skäl, inte för att vi vill ha en prenumeration.

---

## Del 3: Ny topp 10

Rangordnad efter sannolikhet att faktiskt ge pengar, inte efter hur intressant idén är.

### 1. Efterlevnad av tillgänglighetslagen (EAA) för nordisk e-handel och SaaS

**Problem.** Lagen om vissa produkters och tjänsters tillgänglighet trädde i kraft i juni 2025 och omfattar för första gången e-handel, banktjänster och elektronisk kommunikation i privat sektor. Kraven följer WCAG 2.1 AA via EN 301 549. Nästan ingen mindre e-handlare uppfyller dem.

**Bevis på efterfrågan — det starkaste i hela materialet.** PTS har inlett tillsyn och har totalt 28 tillsynsärenden igång sedan 2025, varav 11 nya under 2026. Namngivna bolag inkluderar Ellos, Biltema, KappAhl, Apotea, Åhléns, MQ, Mathem, Apotek Hjärtat, Kronans Apotek, Hemköp och Coop. PTS första breda mätning visade brister i **samtliga** sektorer. Sanktionsmöjligheten är förelägganden med vite och sanktionsavgifter, med tak på 10 MSEK. Detta är inte en trend jag gissar mig till — det är en myndighet som publicerar en lista över vilka den granskar härnäst.

**Nuvarande lösningar och varför de inte täcker.**
- *Overlay-widgets* (accessiBe, UserWay): juridiskt giftiga. FTC bötfällde accessiBe på 1 MUSD för vilseledande marknadsföring, en grupptalan landade på 1,2 MUSD, och 1 416 företag med widget installerad stämdes ändå. Overlays fixar inte strukturella HTML-fel, vilket är merparten av överträdelserna.
- *Enterprise-plattformar* (Siteimprove, Monsido): 15 000–40 000 USD/år för medelstora organisationer. Övervakar och rapporterar — lagar inte koden.
- *Svenska konsultbyråer* (Metamatrix, WCAG Networks, B3, Axess Lab, Digitalist): kompetenta och dyra, projektbaserade, långa ledtider, ingen löpande produkt. De vill inte ha en e-handlare med 40 sidmallar och 300 000 kr i budget.

**Luckan.** Mellan en 3 000 kr/år-widget som ökar den juridiska risken och ett 300 000 kr konsultprojekt finns ingenting för det svenska mellanskiktet — bolag med 20–300 MSEK i omsättning som säljer online. De behöver: en granskningsrapport som håller mot PTS, faktiska kodfixar, en tillgänglighetsredogörelse, och bevis på att det fortsätter stämma efter nästa release.

**Varför AI ger 10x.** Automatiska verktyg (axe-core) hittar 30–40 % av felen men förklarar dem för utvecklare, inte för beslutsfattare, och fixar ingenting. En modell som läser DOM, komponentkod och designsystem kan producera *konkreta patchar* — rätt ARIA, fixad rubrikhierarki, fokushantering, formuläretiketter — och skriva rapporten på svenska mappad mot lagrum. Det är skillnaden mellan "du har 412 fel" och "här är en pull request som tar bort 380 av dem".

**Varför just nu.** Tillsynen pågår just nu, i detta kvartal. Om 18 månader är marknaden antingen mättad eller så har de stora bolagen redan löst det. Fönstret är öppet ungefär 12–24 månader.

**Betyg.** Svårighet 5 | Intäktspotential 9 | Konkurrens 4 (i detta segment) | Global potential 9 (EN 301 549 är identisk i hela EU)

**Ideal första kund.** Svensk e-handlare, 30–150 MSEK omsättning, egen eller inhyrd utvecklare, säljer även till Tyskland eller Danmark, ingen egen tillgänglighetskompetens. Helst någon vars bransch precis fått ett tillsynsärende hos en konkurrent.

**Hur hitta den.** Tre kanaler som alla är gratis:
1. PTS publicerar vilka de granskar. Konkurrenterna till de granskade vet att de står på tur. Det är en färdig lead-lista med inbyggd brådska.
2. Automatiserad skanning av 500 svenska e-handelssajter ger en personlig rapport per bolag — "er kassa går inte att slutföra med tangentbord" är ett e-postämne som öppnas.
3. Digitalbyråer som byggt sajterna får nu frågan från sina kunder och saknar kompetens. De blir återförsäljare, inte konkurrenter.

**Snabbaste vägen till första betalning.** Sälj en granskning, inte en prenumeration. Gratis automatisk skanning → betald djupgranskning 19 900 kr → åtgärdspaket → övervakning 2 900–5 900 kr/mån. Första betalningen kan komma inom 3–4 veckor eftersom kunden köper en tjänst med tydlig leverans, inte ett verktygsabonnemang.

**Affärsmodell.** Hybrid: engångsgranskning (19 900–49 000 kr) + prenumeration för övervakning och redogörelse (2 900–5 900 kr/mån) + åtgärdsarbete på timme eller fastpris. Prenumerationen är äkta återkommande — sajter ändras varje sprint och regressioner är oundvikliga.

**Kunder som krävs.** 5 000 kr/mån = 1–2 kunder. 20 000 kr/mån = 4–7. 50 000 kr/mån = 9–18. Utöver detta tillkommer engångsintäkten på ~20 000 kr per ny kund, vilket i praktiken finansierar hela utvecklingen.

**Sannolikheter.**
- *5 000 kr/mån inom 6 mån: 85 %.* Kräver 1–2 kunder. Med en gratis skanningsrapport som dörröppnare och en namngiven, daterad myndighetsrisk som argument är detta en av de lättaste B2B-säljcykler som finns. Risken är inte efterfrågan, den är att man inte ringer tillräckligt många.
- *20 000 kr/mån inom 12 mån: 60 %.* Kräver 4–7 prenumeranter. Realistiskt om granskningarna konverterar till övervakning i minst hälften av fallen. Nedsidan: kunder som ser granskningen som en engångsplikt och säger nej till abonnemanget. Det är den centrala produktrisken och den ska testas tidigt.
- *50 000 kr/mån inom 24 mån: 45 %.* Kräver 9–18 prenumeranter plus byråkanalen. Kräver också att man går utanför Sverige, sannolikt till Tyskland där böterna går till 100 000 EUR per överträdelse. Fullt görbart men inte automatiskt.

**Vad som skulle göra mig fel.** Om PTS tillsyn stannar vid milda förelägganden mot storbolag och aldrig når mellanskiktet, faller brådskan bort och kvar är en "trevlig att ha"-produkt. Övervaka detta: om det inte kommer ett vitesföreläggande eller en sanktionsavgift inom 12 månader, är hypotesen svagare än den ser ut nu.

---

### 2. Svar på säkerhets- och leverantörsgranskningar (NIS2) för europeiska SMB-leverantörer

**Problem.** NIS2 artikel 21 kräver dokumenterat bevis på att varje leverantörs säkerhetsläge har bedömts. Storbolagen skickar därför ut omfattande säkerhetsformulär till alla underleverantörer före avtalsförnyelse. Ett SaaS-bolag med 25 anställda kan få 4–10 sådana per år, à 150–400 frågor, och varje tar en vecka av CTO:ns tid.

**Nuvarande lösningar.** Conveyor från 9 600 USD/år. Vanta 10 000–25 000 USD/år bara för formulärautomatiseringen. Loopio, byggt för RFP-team. Alla riktade mot bolag som redan har en compliance-funktion.

**Luckan.** Ett europeiskt bolag med 10–60 anställda har inte 100 000 kr/år för detta men har exakt samma problem, och för dem är formuläret en direkt förutsättning för att behålla en kund. Betalningsviljan är kopplad till kontraktsvärdet, inte till budgeten för verktyg.

**Betyg.** Svårighet 5 | Intäktspotential 9 | Konkurrens 5 | Global potential 9

**Ideal första kund.** Europeiskt B2B-SaaS-bolag, 15–60 anställda, säljer till bank, industri eller offentlig sektor, har precis förlorat en vecka på ett formulär.

**Hur hitta den.** LinkedIn-sökning på CTO/CISO i nordiska SaaS-bolag i rätt storleksklass; kommentarsfält där folk klagar på säkerhetsformulär; via de compliance-konsulter som redan hjälper dessa bolag med ISO 27001.

**Snabbaste vägen till betalning.** Gör det manuellt först: "skicka ert nästa formulär till mig, ni får det ifyllt inom 48 timmar, 9 000 kr". Bygg produkten av det man lär sig.

**Pris och modell.** 2 900–7 900 kr/mån för kunskapsbas + obegränsade formulär, alternativt 6 000–12 000 kr per besvarat formulär.

**Kunder.** 5 000 kr/mån = 1–2. 20 000 = 4–7. 50 000 = 9–17.

**Sannolikheter.** 5k inom 6 mån: 65 %. 20k inom 12 mån: 45 %. 50k inom 24 mån: 35 %.
*Motivering:* smärtan är extrem och ACV hög, men köparen är svårare att hitta än i idé 1, säljcykeln längre, och efterfrågan är ryckig — ett bolag som just skickat in ett formulär har inget akut behov på fyra månader. Dessutom rör sig Vanta nedåt i marknaden, vilket är ett reellt hot inom 24 månader.

---

### 3. PDF- och dokumenttillgänglighet för finans, försäkring och offentlig sektor

**Problem.** Samma lagstiftning som i idé 1 omfattar dokument. Banker, försäkringsbolag, kommuner och myndigheter har tiotusentals otillgängliga PDF:er: årsredovisningar, villkor, blanketter, protokoll. Manuell taggning kostar 500–1 500 kr per dokument hos konsult.

**Nuvarande lösningar.** Adobe Acrobat Pro (manuellt, långsamt), CommonLook (dyrt, klumpigt), konsultbyråer per dokument.

**Luckan.** Volymproblem utan volymlösning. AI-modeller kan i dag härleda läsordning, rubriknivåer, tabellstruktur och alt-texter från layout — det som tar en människa 45 minuter per dokument.

**Betyg.** Svårighet 6 | Intäktspotential 8 | Konkurrens 3 | Global potential 8

**Ideal första kund.** Kommun eller försäkringsbolag med 5 000+ publicerade PDF:er och ett tillsynsärende i horisonten.

**Snabbaste vägen till betalning.** Fastpris per dokument (250–600 kr) på en pilot om 100 dokument = 25 000–60 000 kr direkt.

**Pris och modell.** Volympris per dokument, eller abonnemang 8 000–25 000 kr/mån för löpande flöde.

**Kunder.** 5 000 kr/mån = 1 liten kund. 50 000 kr/mån = 3–6 kunder.

**Sannolikheter.** 5k/6 mån: 55 %. 20k/12 mån: 45 %. 50k/24 mån: 35 %.
*Motivering:* mycket hög ACV och nästan ingen konkurrens i mellanskiktet, men offentlig sektor har upphandlingsregler och långa beslutsvägar, och kvalitetskraven på taggning är hårda — en halvbra PDF-taggning är värdelös. Teknisk risk högre än idé 1.

---

### 4. Avtalsbevakning för inköp i mellanstora bolag

**Problem.** Inte engångsanalys av ett avtal (den marknaden är död, se Clausely till 12,99 USD) utan **löpande bevakning av en avtalsportfölj**: uppsägningstider, automatiska förlängningar, prisjusteringsklausuler, indexuppräkningar. Bolag med 80–400 leverantörsavtal förlorar sexsiffriga belopp per år på att missa uppsägningsfönster.

**Luckan.** De stora CLM-systemen (Ironclad, Precisely, Contractbook) säljs till juristavdelningar. Bolag utan juristavdelning har avtalen i en Dropbox-mapp.

**Betyg.** Svårighet 4 | Intäktspotential 7 | Konkurrens 5 | Global potential 8

**Ideal första kund.** Bolag med 50–300 anställda, ekonomichef utan juristfunktion.

**Snabbaste vägen till betalning.** "Skicka era 100 leverantörsavtal, ni får en kalender över alla uppsägningsfönster och en lista på autoförnyelser inom 14 dagar — 25 000 kr." ROI:n är ofta bevisbar i första leveransen.

**Pris och modell.** 3 900–9 900 kr/mån efter en betald genomgång.

**Kunder.** 5 000 = 1. 20 000 = 3–5. 50 000 = 6–13.

**Sannolikheter.** 5k/6 mån: 60 %. 20k/12 mån: 45 %. 50k/24 mån: 30 %.
*Motivering:* värdet är lätt att bevisa i kronor, men det är ett "vitamin" tills bolaget bränt sig, och det finns ingen deadline som tvingar fram beslut. Retention är osäker — när portföljen väl är kartlagd kan kunden uppleva att jobbet är gjort.

---

### 5. AI-inventering och AI-policy enligt AI-förordningen för svenska bolag

**Problem.** Kravet på AI-kunnighet (artikel 4) gäller sedan februari 2025 och deployer-skyldigheter finns oavsett. Bolag vet inte vilka AI-system de faktiskt använder, vem som ansvarar, eller vad de måste dokumentera.

**Varför den hamnar på plats 5 och inte högre.** Deadline för högrisksystem, 2 augusti 2026, är enligt Digital Omnibus-förslaget på väg att skjutas till december 2027. **När deadline flyttas försvinner brådskan**, och därmed betalningsviljan. Efterfrågan finns men den är "vi borde", inte "vi måste nu".

**Betyg.** Svårighet 4 | Intäktspotential 7 | Konkurrens 6 | Global potential 8

**Pris och modell.** 2 900–6 900 kr/mån, eller inventering som engångstjänst 30 000–80 000 kr.

**Sannolikheter.** 5k/6 mån: 55 %. 20k/12 mån: 35 %. 50k/24 mån: 25 %.

---

### 6. Nischad anbudsassistent för en enskild bransch inom offentlig upphandling

**Problem.** Svenska småföretag lämnar anbud sällan, gör fel på skallkrav och förlorar på formalia.

**Verkligheten.** Tendium och Mercell är svenska, finansierade och har AI-sammanfattning av upphandlingsdokument i produktion. Att bygga generellt är kört. Det som återstår är en enda bransch där kravmassan är standardiserad (t.ex. städ, bemanning, VA-entreprenad) och där man kan bygga en kravbibliotek som är bättre än de generella verktygen.

**Betyg.** Svårighet 5 | Intäktspotential 8 | Konkurrens 7 | Global potential 5 (mycket landsspecifikt)

**Sannolikheter.** 5k/6 mån: 45 %. 20k/12 mån: 35 %. 50k/24 mån: 25 %.
*Motivering:* höga kontraktsvärden gör betalningsviljan god, men man tävlar mot finansierade bolag med säljkår, och den nationella inlåsningen begränsar uppsidan.

---

### 7. Tillgänglighetsövervakning som white-label för digitalbyråer

**Problem.** Digitalbyråer får nu frågan från sina kunder och har varken kompetens eller verktyg. De vill sälja tillgänglighet som en tjänst med sitt eget namn på rapporten.

**Varför separat från idé 1.** Det är samma motor men en helt annan affär: en byrå med 30 kunder ger 30 sajter från ett enda säljsamtal. Lägre pris per sajt, dramatiskt bättre distribution.

**Betyg.** Svårighet 4 (om idé 1 finns) | Intäktspotential 8 | Konkurrens 4 | Global potential 9

**Pris och modell.** 900–1 900 kr per sajt och månad, minimum 10 sajter. En byrå = 9 000–19 000 kr/mån.

**Kunder.** 50 000 kr/mån = 3–5 byråer.

**Sannolikheter.** 5k/6 mån: 50 %. 20k/12 mån: 45 %. 50k/24 mån: 40 %.
*Motivering:* längre säljcykel initialt men mycket bättre skalning. Detta är sannolikt kanal två för idé 1, inte ett eget bolag.

---

### 8. Support-QA för nordiska e-handlare

**Problem.** Ingen vet om supportsvaren är korrekta; stickprov på 2 % av ärendena är standard.

**Varför bara plats 8.** Zendesk köpte Klaus och buntar QA i sin WEM-svit. MaestroQA, EvaluAgent och Lorikeet delar resten. Segmentet är bemannat, och nordiska e-handlare med egen supportavdelning stor nog att behöva QA är ganska få.

**Betyg.** Svårighet 5 | Intäktspotential 7 | Konkurrens 7 | Global potential 8

**Sannolikheter.** 5k/6 mån: 45 %. 20k/12 mån: 30 %. 50k/24 mån: 20 %.

---

### 9. Beredskap för e-fakturamandat i Frankrike, Belgien och Polen

**Problem.** Belgien kräver Peppol-baserad B2B-e-fakturering sedan 1 januari 2026, oavsett bolagsstorlek. Polens KSeF gäller stora bolag från 1 februari 2026 och mindre från 1 april 2026. Frankrike kräver att **alla** franska bolag kan ta emot e-fakturor från 1 september 2026. Det är om fem veckor.

**Varför bara plats 9 trots perfekt timing.** Det här är infrastruktur. Frankrike kräver certifierade plattformar (PDP), Polen har en clearingmodell där skattemyndigheten godkänner varje faktura. Bokförings- och ERP-leverantörerna kommer att bunta detta gratis, för de måste. En ensam grundare som bygger här bygger på mark som Fortnox, Pennylane, Sage och Qonto redan äger.

**Betyg.** Svårighet 7 | Intäktspotential 8 | Konkurrens 8 | Global potential 9

**Sannolikheter.** 5k/6 mån: 40 %. 20k/12 mån: 25 %. 50k/24 mån: 15 %.

---

### 10. Regelbevakning för små bolag i reglerade branscher

**Problem.** Föreskrifter ändras och små bolag i fintech, vård, livsmedel och miljö missar det.

**Betyg.** Svårighet 4 | Intäktspotential 7 | Konkurrens 4 | Global potential 6

**Varför sist.** Bevakning utan handling är en nyhetsprenumeration, och nyhetsprenumerationer churnar hårt. Värdet uppstår först när produkten också säger vad bolaget ska *göra*, vilket kräver domänkunskap per bransch och därmed förhindrar bredd.

**Sannolikheter.** 5k/6 mån: 45 %. 20k/12 mån: 30 %. 50k/24 mån: 20 %.

---

## Del 4: Beslutet

### Vald idé: Efterlevnad av tillgänglighetslagen för nordisk e-handel

Motivering mot de fem kriterierna:

| Kriterium | Bedömning |
|---|---|
| Hög sannolikhet att lyckas | Efterfrågan är inte hypotetisk. En myndighet driver 28 tillsynsärenden och publicerar namnen. Detta är den enda kandidaten där jag kan peka på vem som köper och varför de köper i år. |
| Låg utvecklingsrisk | Grunden är axe-core (öppen källkod, beprövad). Standarden EN 301 549 och WCAG 2.2 är offentliga och stabila. Inget forskningsprojekt — den svåra delen är rapportkvalitet och kodfixar, båda verifierbara. |
| Snabb väg till intäkter | Första betalningen är en granskning, inte ett abonnemang. Det korta säljsamtalet är "här är fyra fel på er kassa, PTS granskar er bransch, vill ni ha hela listan?" |
| Skalbarhet | EN 301 549 gäller identiskt i 27 länder. Tyskland bötfäller upp till 100 000 EUR per överträdelse, Frankrike upp till 250 000 EUR. Byråkanalen multiplicerar per säljsamtal. |
| Litet team | En person kan köra skanning, rapportgenerering och åtgärdsförslag. Åtgärdsarbetet kan läggas ut eller lämnas till kundens utvecklare. |

### Kritisk självprövning — de fyra bästa argumenten mot mitt eget val

**1. "Det är en konsulttjänst förklädd till SaaS."** Delvis sant, och det är avsiktligt. Med målet 5 000–50 000 kr/mån är en produktifierad tjänst med hög ACV en snabbare väg än ren SaaS med låg ACV. Men risken är verklig: om granskningen aldrig konverterar till abonnemang bygger man ett konsultbolag med tak för hur mycket man orkar. **Detta är den viktigaste sak som ska testas i vecka 6–10, inte i månad 18.** Testet är enkelt: erbjud abonnemanget vid leverans av de tre första granskningarna och räkna hur många som säger ja.

**2. "Siteimprove är nordiskt och kan gå ner i pris."** De kan, men de har byggt en enterprise-säljorganisation och en prislapp på 15 000–40 000 USD/år. Att sälja för 3 000 kr/mån förstör deras marginalstruktur och deras säljare vill inte ta samtalen. Det är den klassiska situationen där en etablerad aktör *kan* men inte *vill*. Det skyddet håller i några år, inte för alltid.

**3. "Tillgänglighet kräver certifierad expertis som jag inte har."** Delvis. Automatiska verktyg fångar 30–40 % av felen; resten kräver manuell testning med skärmläsare och tangentbord. Det går att lära sig på 4–8 veckor för de vanligaste e-handelsmönstren (kassa, produktfilter, formulär, modaler), och det är precis därför konkurrensen från helgbyggare uteblir. Men man ska inte sälja "garanterad efterlevnad" innan man kan leverera det — overlay-branschens öde visar exakt vad som händer med den som gör det.

**4. "Marknaden kan vara löst om 24 månader."** Möjligt. Storbolagen kommer att fixa sina sajter. Men mellanskiktet är tusentals bolag, nya sajter byggs varje vecka, regressioner uppstår vid varje release, och EU:s krav utvidgas snarare än krymper. Det som är en engångsvåg är granskningsintäkten; det som är uthålligt är övervakningen.

### Vad jag uttryckligen avråder från

Testet som föreslogs — sälj ett Excelark för 390–790 kr på Gumroad — validerar fel sak. Att någon spenderar priset av en lunch bevisar inte att ett företag betalar 3 000 kr/mån. Ett bättre 48-timmarstest med samma ansträngning: skanna 50 svenska e-handelssajter automatiskt, skicka en personlig rapport med tre konkreta fel till var och en, och erbjud en fullständig granskning för 19 900 kr. Ett enda ja är ett hundra gånger starkare köpbevis än femtio Gumroad-försäljningar.

### Konkret 14-dagarsplan

| Dag | Vad | Utfall |
|---|---|---|
| 1–2 | Skanningsskript med axe-core + Playwright mot 50 svenska e-handelssajter, inklusive kassaflödet | Rådata på faktiska överträdelser |
| 3–4 | Rapportgenerator: LLM översätter tekniska fel till svensk rapport mappad mot lagkrav, med skärmdumpar | En rapport som en vd förstår |
| 5–6 | Landningssida + tre priser. Ingen produkt, bara erbjudandet | Något att länka till |
| 7–10 | 50 personliga utskick med bifogad minirapport, plus 20 samtal | 3–5 möten |
| 11–14 | Möten. Sälj granskning för 19 900 kr. Erbjud abonnemang redan här | Första betalningen eller ett tydligt nej |

**Beslutspunkt efter dag 14:** noll betalande av 50 kontaktade betyder att erbjudandet, priset eller målgruppen är fel — inte att man ska bygga mer produkt. En betalande kund betyder att man bygger vidare på riktigt.

---

## Källor

- PTS tillsyn av e-handelstjänster och tillgänglighetslagen — [pts.se](https://pts.se/digital-inkludering/lagen-om-vissa-produkters-och-tjansters-tillganglighet/pts-tillsyn/), [PTS granskar ytterligare 11 e-handelstjänster](https://pts.se/nyheter-och-pressmeddelanden/pts-granskar-ytterligare-11-e-handelstjansters-tillganglighet/), [PTS första breda mätning](https://www.pts.se/nyheter-och-pressmeddelanden/pts-forsta-breda-matning-av-tillgangligheten-pa-svenska-webbplatser/)
- Overlay-risker och FTC-förlikning — [216digital](https://216digital.com/the-hidden-risks-of-accessibility-overlays-why-the-quick-fix-is-a-legal-liability-in-2026/), [TestParty](https://testparty.ai/blog/why-800-businesses-with-accessibe-were-still-sued), [RatedWithAI om FTC-boten](https://ratedwithai.com/blog/accessibe-review-2026)
- EAA-böter per land — [web-accessibility-checker.com](https://web-accessibility-checker.com/en/blog/eaa-fines-penalties-by-country), [Level Access](https://www.levelaccess.com/compliance-overview/european-accessibility-act-eaa/)
- Siteimprove-prissättning — [Vendr](https://www.vendr.com/marketplace/siteimprove), [TestParty](https://testparty.ai/blog/siteimprove-alternatives)
- Svenska tillgänglighetskonsulter — [Metamatrix](https://metamatrix.se/tjanster/tillganglighet/), [WCAG Networks](https://www.wcagnetworks.com/tillganglighetsgranskning/), [B3](https://b3.se/erbjudande/specialistomraden/webb-design-och-e-handel/digital-tillganglighet/tillganglighetsgranskning), [Axess Lab](https://axesslab.com/)
- Konkurrenter i de förkastade nischerna — [Bliqat](https://bliqat.com/for/bygg), [Smidia](https://smidia.se/), [Supergrow-jämförelse](https://www.supergrow.ai/blog/linkedin-carousel-generators), [MRRSaver](https://www.mrrsaver.com/alternatives/churnkey), [Reply Champion](https://www.replychampion.com/best-ai-review-response-tool), [TalentVeil](https://talentveil.com/), [CVFormatter](https://www.cvformatter.co/), [Clausely](https://clausely.app/blog/best-ai-contract-review-tools), [LinkBoss](https://linkboss.io/blog/best-internal-linking-tools/)
- Fortnox AI-fakturatolkning och BLINK — [Revisionsvärlden](https://revisionsvarlden.se/digitalt/fortnox-slapper-ai-tolkning-av-fakturor/), [Fortnox-förändringar 2026](https://redovisning.ai/guider/fortnox-forandringar-2026)
- Säkerhetsformulär-automatisering, priser — [Conveyor på G2](https://www.g2.com/products/conveyor-conveyor/pricing), [Vanta-prissättning](https://costbench.com/software/compliance-management/vanta/)
- NIS2 leverantörskrav — [3rdRisk](https://www.3rdrisk.com/blog/seven-nis2-questions-to-ask), [Sunbytes om artikel 21](https://sunbytes.io/blog/cybersecurity/nis2-article-21-requirements-explained/)
- E-fakturamandat 2026 — [Invoice Navigator](https://www.invoicenavigator.eu/deadlines), [SPS Commerce](https://www.spscommerce.com/community/articles/e-invoicing-mandates-in-europe-the-2026-business-guide)
- AI-förordningens uppskjutna deadline — [Travers Smith](https://www.traverssmith.com/knowledge/knowledge-container/eu-agrees-to-delay-key-ai-act-compliance-deadlines/), [DLA Piper](https://knowledge.dlapiper.com/dlapiperknowledge/globalemploymentlatestdevelopments/2026/The-Digital-AI-Omnibus-Proposed-deferral-of-high-risk-AI-obligations-under-the-AI-Act)
- Marknadsläget för AI-wrappers — [saas.group](https://saas.group/blog/ai-didnt-break-saas-it-just-made-your-moat-visible/), [Indie Hackers SaaS-rapport 2026](https://www.indiehackers.com/post/2026-saas-market-report-key-insights-95423fc66b)
- Svensk e-handel — [PostNord](https://www.postnord.se/om-oss/nyheter-press-och-artiklar/2026/rekordar-for-svensk-e-handel---hogsta-omsattningen-nagonsin/), [Svensk Handel](https://www.svenskhandel.se/rapporter/e-handelsindikatorn/)
- GEO/AI-synlighet, marknadsmättnad — [Rankability](https://www.rankability.com/blog/best-ai-search-visibility-tracking-tools/), [Surmado](https://www.surmado.com/blog/best-ai-visibility-tools-2026)
