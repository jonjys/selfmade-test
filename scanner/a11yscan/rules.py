"""Översättning av axe-core-regler till svenska, med koppling till WCAG och lagkrav.

Syftet är att en vd ska förstå rapporten utan att kunna WCAG. Varje regel får en
svensk rubrik, en affärsmässig konsekvens och en referens till det
framgångskriterium i WCAG 2.1 AA som EN 301 549 hänvisar till.

Regler som inte finns här faller tillbaka på axe-cores egen engelska
beskrivning — det är bättre än att tappa bort dem, men de bör översättas
efterhand som de dyker upp i verkliga skanningar.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RuleInfo:
    """Svensk beskrivning av en axe-core-regel."""

    rubrik: str
    konsekvens: str
    wcag: str


# Prioritetsordning för allvarlighetsgrad. Används för sortering i rapporten.
IMPACT_ORDER = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}

IMPACT_SV = {
    "critical": "Kritisk",
    "serious": "Allvarlig",
    "moderate": "Måttlig",
    "minor": "Mindre",
}

# De regler som i praktiken dominerar utfallet på e-handelssajter.
RULES: dict[str, RuleInfo] = {
    "image-alt": RuleInfo(
        rubrik="Bilder saknar alternativtext",
        konsekvens=(
            "En skärmläsare läser upp filnamnet i stället för vad bilden visar. "
            "På en produktsida innebär det att kunden inte får veta vad hen köper."
        ),
        wcag="1.1.1 Icke-textuellt innehåll (A)",
    ),
    "color-contrast": RuleInfo(
        rubrik="För låg kontrast mellan text och bakgrund",
        konsekvens=(
            "Texten går inte att läsa för den som har nedsatt syn, vilket i "
            "praktiken gäller en stor del av kundgruppen över 60 år."
        ),
        wcag="1.4.3 Kontrast, minimum (AA)",
    ),
    "label": RuleInfo(
        rubrik="Formulärfält saknar etikett",
        konsekvens=(
            "Skärmläsaren kan inte tala om vad fältet ska innehålla. I en kassa "
            "betyder det att beställningen inte går att slutföra."
        ),
        wcag="3.3.2 Ledtexter eller instruktioner (A)",
    ),
    "link-name": RuleInfo(
        rubrik="Länkar saknar läsbar text",
        konsekvens=(
            "Länken läses upp som \"länk\" utan mål. Navigering med skärmläsare "
            "bygger på att kunna hoppa mellan länkar."
        ),
        wcag="2.4.4 Länkens syfte (A)",
    ),
    "button-name": RuleInfo(
        rubrik="Knappar saknar läsbar text",
        konsekvens=(
            "En ikonknapp utan text — t.ex. varukorgen eller stäng-krysset — är "
            "helt osynlig för skärmläsare."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "html-has-lang": RuleInfo(
        rubrik="Sidan saknar språkangivelse",
        konsekvens=(
            "Skärmläsaren läser svensk text med engelskt uttal och blir "
            "obegriplig. En rad kod att åtgärda."
        ),
        wcag="3.1.1 Sidans språk (A)",
    ),
    "html-lang-valid": RuleInfo(
        rubrik="Ogiltig språkkod",
        konsekvens=(
            "Språkkoden går inte att tolka, så skärmläsaren läser texten med fel "
            "uttal precis som om angivelsen saknats helt."
        ),
        wcag="3.1.1 Sidans språk (A)",
    ),
    "heading-order": RuleInfo(
        rubrik="Rubriknivåerna hoppar över steg",
        konsekvens=(
            "Skärmläsaranvändare navigerar via rubriker. Fel ordning gör att "
            "sidans struktur inte går att förstå."
        ),
        wcag="1.3.1 Information och relationer (A)",
    ),
    "aria-required-attr": RuleInfo(
        rubrik="ARIA-roll saknar obligatoriska attribut",
        konsekvens=(
            "Komponenten presenteras felaktigt för hjälpmedel, vilket ofta är "
            "värre än att inte ha någon ARIA alls."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-valid-attr-value": RuleInfo(
        rubrik="Ogiltigt värde i ARIA-attribut",
        konsekvens="Hjälpmedlet får motstridig information och kan bete sig oförutsägbart.",
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-hidden-focus": RuleInfo(
        rubrik="Dolt element går att nå med tangentbord",
        konsekvens=(
            "Fokus försvinner till något användaren inte kan se. Det här är en "
            "vanlig orsak till att kunder fastnar i menyer och modaler."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "region": RuleInfo(
        rubrik="Innehåll ligger utanför landmärken",
        konsekvens="Går inte att hoppa direkt till huvudinnehållet.",
        wcag="1.3.1 Information och relationer (A)",
    ),
    "landmark-one-main": RuleInfo(
        rubrik="Sidan saknar ett huvudinnehåll",
        konsekvens="Användaren tvingas tabba genom hela menyn på varje sidladdning.",
        wcag="1.3.1 Information och relationer (A)",
    ),
    "list": RuleInfo(
        rubrik="Felaktigt uppbyggd lista",
        konsekvens="Skärmläsaren annonserar fel antal produkter i en listning.",
        wcag="1.3.1 Information och relationer (A)",
    ),
    "duplicate-id-active": RuleInfo(
        rubrik="Dubblerade id på interaktiva element",
        konsekvens="Etiketter kopplas till fel fält, vilket ger fel uppläsning i formulär.",
        wcag="4.1.1 Parsning (A)",
    ),
    "select-name": RuleInfo(
        rubrik="Rullgardinsmeny saknar etikett",
        konsekvens=(
            "Storleks- och variantväljare blir omöjliga att använda med "
            "skärmläsare — en direkt förlorad order."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "frame-title": RuleInfo(
        rubrik="Inbäddad ram saknar titel",
        konsekvens="Vanligt i betalfönster och chattwidgetar; ramen blir oidentifierbar.",
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "meta-viewport": RuleInfo(
        rubrik="Zoom är avstängd",
        konsekvens=(
            "Användare som behöver förstora texten kan inte göra det på mobil. "
            "Ett attribut att ta bort."
        ),
        wcag="1.4.4 Ändring av textstorlek (AA)",
    ),
    "input-image-alt": RuleInfo(
        rubrik="Bildknapp saknar alternativtext",
        konsekvens="Sökknappar av bildtyp blir oanvändbara med skärmläsare.",
        wcag="1.1.1 Icke-textuellt innehåll (A)",
    ),
    "form-field-multiple-labels": RuleInfo(
        rubrik="Fält har flera motstridiga etiketter",
        konsekvens="Uppläsningen blir tvetydig och kunden fyller i fel uppgift.",
        wcag="3.3.2 Ledtexter eller instruktioner (A)",
    ),
    "scrollable-region-focusable": RuleInfo(
        rubrik="Rullningsbar yta går inte att nå med tangentbord",
        konsekvens="Innehåll som kräver scroll blir oåtkomligt utan mus.",
        wcag="2.1.1 Tangentbord (A)",
    ),
    # Nedanstående regler saknade svensk text tills de dök upp i skarpa
    # körningar mot svenska e-handelssajter. Ordningen följer hur ofta de
    # faktiskt förekom.
    "link-in-text-block": RuleInfo(
        rubrik="Länkar i löpande text syns bara på färgen",
        konsekvens=(
            "En länk mitt i en textmassa måste gå att urskilja på något mer än "
            "färgen — annars ser den som är färgblind ingen länk alls. "
            "Understrykning räcker."
        ),
        wcag="1.4.1 Användning av färg (A)",
    ),
    "listitem": RuleInfo(
        rubrik="Listpunkter ligger utanför sin lista",
        konsekvens=(
            "Skärmläsaren annonserar hur många punkter en lista har. Ligger de "
            "fel får kunden höra fel antal produkter, eller inget alls."
        ),
        wcag="1.3.1 Information och relationer (A)",
    ),
    "nested-interactive": RuleInfo(
        rubrik="Knapp eller länk inuti en annan knapp",
        konsekvens=(
            "Två klickbara element inuti varandra gör att hjälpmedel inte kan "
            "avgöra vad som faktiskt aktiveras. Vanligt i produktkort där hela "
            "kortet är en länk och köpknappen ligger inuti."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-required-parent": RuleInfo(
        rubrik="ARIA-komponent saknar sin förälder",
        konsekvens=(
            "En roll som tab eller option måste ligga i rätt sorts behållare. "
            "Gör den inte det presenteras komponenten som trasig för "
            "skärmläsaren, ofta helt utan att det syns visuellt."
        ),
        wcag="1.3.1 Information och relationer (A)",
    ),
    "aria-required-children": RuleInfo(
        rubrik="ARIA-komponent saknar rätt innehåll",
        konsekvens=(
            "Behållaren har rätt roll men innehållet i den har fel roll, till "
            "exempel en lista vars punkter inte är listpunkter. Hjälpmedlet "
            "presenterar då komponenten som trasig."
        ),
        wcag="1.3.1 Information och relationer (A)",
    ),
    "aria-allowed-attr": RuleInfo(
        rubrik="ARIA-attribut som inte hör till rollen",
        konsekvens=(
            "Attributet ignoreras i bästa fall och förvirrar hjälpmedlet i "
            "sämsta. Det är oftast en rest från en tidigare version av "
            "komponenten."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-prohibited-attr": RuleInfo(
        rubrik="ARIA-attribut som är förbjudet på elementet",
        konsekvens=(
            "Specifikationen förbjuder uttryckligen attributet på den här sortens "
            "element. Det ignoreras i bästa fall och förvirrar hjälpmedlet i värsta."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-input-field-name": RuleInfo(
        rubrik="Egenbyggt inmatningsfält saknar namn",
        konsekvens=(
            "En komponent med roll som combobox eller slider men utan namn "
            "läses upp som bara sin roll. Kunden hör 'kombinationsruta' utan "
            "att få veta vad den gäller."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "aria-roles": RuleInfo(
        rubrik="Ogiltig ARIA-roll",
        konsekvens=(
            "Rollen finns inte i specifikationen. Elementet presenteras då med sin "
            "ursprungliga roll, eller ingen alls."
        ),
        wcag="4.1.2 Namn, roll, värde (A)",
    ),
    "document-title": RuleInfo(
        rubrik="Sidan saknar titel",
        konsekvens=(
            "Titeln är det första en skärmläsare säger vid sidbyte, och det som "
            "står i webbläsarfliken. Utan den vet kunden inte var hen hamnat."
        ),
        wcag="2.4.2 Sidans titel (A)",
    ),
    "target-size": RuleInfo(
        rubrik="För små klickytor",
        konsekvens="Svårt att träffa för den med nedsatt motorik, särskilt på mobil.",
        wcag="2.5.8 Målstorlek, minimum (AA)",
    ),
}

# Egna kontroller utöver axe-core. Dessa fångar sådant som automatiska verktyg
# normalt missar och som är den vanligaste orsaken till att en kassa inte går
# att slutföra utan mus.
CUSTOM_RULES: dict[str, RuleInfo] = {
    "custom-click-handler-not-focusable": RuleInfo(
        rubrik="Klickbara element går inte att nå med tangentbord",
        konsekvens=(
            "Ett element som byggts som en knapp med en klickhanterare, i stället "
            "för en riktig knapp, fungerar med mus men inte med tangentbord. "
            "Sitter det i kassan eller i varianturvalet kan kunden inte handla alls."
        ),
        wcag="2.1.1 Tangentbord (A)",
    ),
    "custom-no-skip-link": RuleInfo(
        rubrik="Ingen genväg till huvudinnehållet",
        konsekvens=(
            "Tangentbordsanvändare måste tabba genom hela menyn på varje sida. "
            "På en sajt med stor meny betyder det 40+ tryck per sidladdning."
        ),
        wcag="2.4.1 Hoppa över block (A)",
    ),
    "custom-placeholder-som-etikett": RuleInfo(
        rubrik="Fält använder platshållartext i stället för etikett",
        konsekvens=(
            "Texten försvinner så fort kunden börjar skriva, och den som blir "
            "avbruten mitt i en beställning vet inte längre vad fältet gäller. "
            "Notera att axe-core godkänner det här — placeholder räknas som "
            "tillgängligt namn enligt specen, trots att det är ett reellt "
            "problem. Det är ett exempel på varför en ren maskinskanning inte "
            "räcker."
        ),
        wcag="3.3.2 Ledtexter eller instruktioner (A)",
    ),
    "custom-no-visible-focus": RuleInfo(
        rubrik="Fokusmarkering är borttagen",
        konsekvens=(
            "Den som navigerar med tangentbord ser inte var hen befinner sig. "
            "Orsakas nästan alltid av CSS-regeln outline: none."
        ),
        wcag="2.4.7 Synligt fokus (AA)",
    ),
}


def slå_upp(regel_id: str) -> RuleInfo | None:
    """Returnerar svensk beskrivning för en regel, eller None om den saknas."""
    return RULES.get(regel_id) or CUSTOM_RULES.get(regel_id)
