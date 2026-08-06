/**
 * Läser skanningsdatan som Python-skannern exporterar.
 *
 * Datan är en statisk JSON-fil som checkas in. Det är avsiktligt: en
 * prenumerationsprodukt som ska tjäna pengar utan tillsyn ska ha så få
 * rörliga delar som möjligt. En databas hade krävt drift, uppdateringar och
 * en jourlinje — allt sådant som gör att en produkt slutar vara passiv.
 */

import kunddata from "@/data/kunder.json";

export type Allvarlighet = "critical" | "serious" | "moderate" | "minor";

export interface Brist {
  regelId: string;
  rubrik: string;
  konsekvens: string;
  wcag: string;
  allvarlighet: Allvarlighet;
  antal: number;
  sidtyp: string;
}

export interface Mätpunkt {
  datum: string;
  totalt: number;
  allvarliga: number;
}

export interface Kund {
  /** Domänen, och samtidigt nyckeln i URL:en. */
  doman: string;
  /** Vad kunden heter, för rubriken. Faller tillbaka på domänen. */
  namn: string;
  senastSkannad: string;
  totalt: number;
  allvarliga: number;
  /** Historik, äldst först. Två punkter räcker för att rita en riktning. */
  historik: Mätpunkt[];
  brister: Brist[];
  /** Regel-id som tillkommit sedan förra körningen. */
  nya: string[];
  /** Regel-id som försvunnit sedan förra körningen. */
  lagade: string[];
}

const kunder = kunddata as unknown as Kund[];

export function allaKunder(): Kund[] {
  return [...kunder].sort((a, b) => b.allvarliga - a.allvarliga);
}

export function hämtaKund(doman: string): Kund | undefined {
  return kunder.find((k) => k.doman === doman);
}

/**
 * Riktningen sedan förra mätningen.
 *
 * Vi returnerar aldrig "bra" enbart för att siffran är låg — bara för att den
 * gått ned. En sajt med fyra kvarstående fel har inte blivit bra, den har
 * blivit bättre, och skillnaden spelar roll när kunden läser.
 */
export function riktning(kund: Kund): {
  status: "bättre" | "sämre" | "oförändrat" | "första";
  skillnad: number;
} {
  if (kund.historik.length < 2) return { status: "första", skillnad: 0 };
  const [näst, senast] = kund.historik.slice(-2);
  const skillnad = senast.totalt - näst.totalt;
  if (skillnad > 0) return { status: "sämre", skillnad };
  if (skillnad < 0) return { status: "bättre", skillnad };
  return { status: "oförändrat", skillnad: 0 };
}

export const ALLVARLIGHET_SV: Record<Allvarlighet, string> = {
  critical: "Kritisk",
  serious: "Allvarlig",
  moderate: "Måttlig",
  minor: "Mindre",
};

/** Svenskt tusentalsavgränsare: hårt mellanslag, aldrig komma. */
export function tal(n: number): string {
  return n.toLocaleString("sv-SE").replace(/ /g, " ");
}
