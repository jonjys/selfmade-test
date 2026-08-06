/**
 * Var förfrågningarna hamnar.
 *
 * Adressen står på ett enda ställe. Den ligger i klartext på sidan ändå, så
 * det finns ingen hemlighet att skydda — poängen är att den som ska byta den
 * bara behöver hitta ett ställe.
 *
 * Två sätt att sätta den:
 *   1. NEXT_PUBLIC_MOTTAGARE som miljövariabel (i Vercels projektinställningar)
 *   2. Byt PLATSHÅLLARE här nedan
 *
 * Använd en adress på egen domän. En granskningstjänst som svarar från en
 * gmail ser inte ut som en granskningstjänst.
 */

const PLATSHÅLLARE = "hej@example.se";

export const MOTTAGARE = process.env.NEXT_PUBLIC_MOTTAGARE || PLATSHÅLLARE;

/**
 * Falskt så länge adressen är kvar som platshållare.
 *
 * Formuläret får aldrig öppna ett mejlfönster till en påhittad adress. En
 * besökare som ser det tappar förtroendet direkt, och det är svårt att vinna
 * tillbaka. Bättre att säga rakt ut att sidan inte är färdigkonfigurerad.
 */
export const ÄR_KONFIGURERAD = !MOTTAGARE.includes("example.se");

/** Domänen som besökaren skrev, utan protokoll, sökväg och inledande www. */
export function städaDomän(rå: string): string {
  return rå
    .trim()
    .replace(/^[a-z]+:\/\//i, "")
    .replace(/^www\./i, "")
    .replace(/\/.*$/, "")
    .toLowerCase();
}

/**
 * Duger strängen som en webbadress?
 *
 * Avsiktligt tillåtande. Ett formulär som avvisar en potentiell kund för att
 * regexen var för sträng kostar mer än ett felskrivet mejl gör.
 */
export function serUtSomDomän(rå: string): boolean {
  const d = städaDomän(rå);
  return /^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(d) && d.length >= 4;
}

export function mejllänk(domän: string): string {
  const ämne = `Skanning av ${domän}`;
  const text =
    `Hej,\n\nJag vill ha en kostnadsfri tillgänglighetsskanning av ` +
    `${domän}.\n\nHälsningar\n`;
  return (
    `mailto:${MOTTAGARE}` +
    `?subject=${encodeURIComponent(ämne)}` +
    `&body=${encodeURIComponent(text)}`
  );
}
