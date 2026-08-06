import Link from "next/link";
import FokusDemo from "./FokusDemo";
import { allaKunder } from "@/lib/data";

export default function Start() {
  const kunder = allaKunder();

  return (
    <>
      <section className="border-b border-linje px-6 py-16 sm:py-24">
        <div className="mx-auto max-w-2xl">
          <Etikett>Tillgänglighetslagen · e-handel</Etikett>
          <h1 className="font-display text-[clamp(2.4rem,6.5vw,3.9rem)] font-semibold leading-[1.04] tracking-tight text-balance">
            Går er kassa att slutföra utan mus?
          </h1>
          <p className="mt-5 max-w-lg text-lg text-dimma">
            Sedan juni 2025 omfattas e-handel av tillgänglighetslagen.
            Post- och telestyrelsen har inlett tillsyn, och de flesta svenska
            butiker klarar inte kraven. Vi visar var det brister — och vad det
            kostar att laga.
          </p>
          <FokusDemo />
          <p className="mt-4 text-sm text-dimma">
            Stäng av vippan och tabba igen. Fältet är fortfarande markerat —
            men ingen ser det. Det är vad en enda CSS-rad,{" "}
            <code>outline: none</code>, gör med en kassa.
          </p>
        </div>
      </section>

      <section className="border-b border-linje px-6 py-16">
        <div className="mx-auto max-w-2xl">
          <Etikett>Tillsynen pågår nu</Etikett>
          <h2 className="font-display text-3xl font-semibold tracking-tight text-balance">
            PTS granskar svensk e-handel, bransch för bransch
          </h2>
          <p className="mt-4">
            Det här är inte en framtida risk. Post- och telestyrelsen har
            öppnat tillsynsärenden mot namngivna handlare — bland dem Apotea,
            Coop, Mathem, Åhléns, Biltema, Ellos och KappAhl. Myndighetens
            första breda mätning visade brister i samtliga granskade sektorer.
          </p>
          <dl className="my-8 grid gap-px overflow-hidden rounded border border-linje bg-linje sm:grid-cols-3">
            <Siffra tal="28" text="tillsynsärenden öppnade sedan 2025" />
            <Siffra tal="11" text="nya e-handelstjänster granskade under 2026" />
            <Siffra tal="10 M" text="kronor är takbeloppet för sanktionsavgift" />
          </dl>
          <p className="text-sm text-dimma">
            Källa: Post- och telestyrelsen. Vid tillsyn kontrolleras att
            webbplatsen uppfyller WCAG-principerna, och PTS kan besluta om
            förelägganden med vite och sanktionsavgifter.
          </p>
        </div>
      </section>

      {kunder.length > 0 && (
        <section className="border-b border-linje px-6 py-16">
          <div className="mx-auto max-w-3xl">
            <Etikett>Under bevakning</Etikett>
            <h2 className="font-display text-3xl font-semibold tracking-tight text-balance">
              Så här ser det ut för sajterna vi följer
            </h2>
            <p className="mt-4 max-w-xl text-dimma">
              Varje sajt skannas om varje vecka. Kunden får ett mejl bara när
              något faktiskt blivit sämre — och sin egen statussida att titta
              på när som helst.
            </p>
            <ul className="mt-8 grid gap-3">
              {kunder.slice(0, 8).map((k) => (
                <li key={k.doman}>
                  <Link
                    href={`/status/${k.doman}/`}
                    className="flex flex-wrap items-baseline justify-between gap-3 rounded border border-linje bg-kort px-5 py-4 no-underline transition-colors hover:border-signal"
                  >
                    <span className="font-semibold">{k.namn}</span>
                    <span className="text-sm text-dimma">
                      <b
                        className={
                          k.allvarliga > 0 ? "text-larm" : "text-signal"
                        }
                      >
                        {k.allvarliga}
                      </b>{" "}
                      allvarliga · {k.totalt} element totalt
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      <section className="border-b border-linje px-6 py-16">
        <div className="mx-auto max-w-4xl">
          <Etikett>Vad det kostar</Etikett>
          <h2 className="font-display text-3xl font-semibold tracking-tight text-balance">
            Fast pris på granskningen. Övervakningen är frivillig.
          </h2>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <Pris
              namn="Skanning"
              belopp="0 kr"
              enhet="engångs, inget konto"
              punkter={[
                "Automatisk genomgång av startsida, produktsida och kassa",
                "De tre allvarligaste bristerna, med skärmbild",
                "Svar inom ett dygn",
              ]}
            />
            <Pris
              markerad
              namn="Granskning"
              belopp="19 900 kr"
              enhet="engångs"
              punkter={[
                "Manuell testning med skärmläsare och enbart tangentbord",
                "Fullständig rapport mot WCAG 2.1 AA och EN 301 549",
                "Prioriterad åtgärdslista till utvecklaren",
                "Underlag till tillgänglighetsredogörelse",
              ]}
            />
            <Pris
              namn="Övervakning"
              belopp="2 900 kr"
              enhet="per månad, från"
              punkter={[
                "Automatisk omskanning varje vecka",
                "Larm när en ny release återinför en brist",
                "Egen statussida med utveckling över tid",
              ]}
            />
          </div>
        </div>
      </section>

      <section className="px-6 py-16">
        <div className="mx-auto max-w-2xl">
          <Etikett>Ärligheten</Etikett>
          <h2 className="font-display text-3xl font-semibold tracking-tight">
            Vad vi inte lovar
          </h2>
          <ul className="mt-6 grid gap-5">
            <Punkt rubrik="Vi lovar inte att ni blir godkända">
              Ingen leverantör kan garantera efterlevnad, och den som gör det
              säger något som inte går att hålla.
            </Punkt>
            <Punkt rubrik="Skanningen hittar inte allt">
              Automatiska verktyg fångar ungefär en tredjedel av bristerna.
              Resten kräver att en människa testar med skärmläsare och
              tangentbord. Det står i varje rapport vi skickar.
            </Punkt>
            <Punkt rubrik="Rapporten är inget juridiskt utlåtande">
              Den beskriver tekniska brister mot en standard. Vad en
              tillsynsmyndighet skulle besluta är en annan fråga.
            </Punkt>
          </ul>
        </div>
      </section>

      <footer className="border-t border-linje px-6 py-10 text-sm text-dimma">
        <div className="mx-auto max-w-2xl">
          Granskningarna görs mot WCAG 2.1 AA och EN 301 549, de standarder
          tillgänglighetslagen hänvisar till. Skanningen bygger på axe-core
          från Deque Systems samt egna kontroller för tangentbordsnavigering.
        </div>
      </footer>
    </>
  );
}

function Etikett({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-5 flex items-center gap-3 text-xs font-bold uppercase tracking-[0.17em] text-signal">
      {children}
      <span aria-hidden="true" className="h-px flex-1 bg-linje" />
    </p>
  );
}

function Siffra({ tal, text }: { tal: string; text: string }) {
  return (
    <div className="bg-kort px-5 py-6">
      <dt className="sr-only">{text}</dt>
      <dd>
        <span className="block font-display text-4xl leading-none tracking-tight tabular-nums">
          {tal}
        </span>
        <span className="mt-2 block text-sm text-dimma">{text}</span>
      </dd>
    </div>
  );
}

function Pris({
  namn,
  belopp,
  enhet,
  punkter,
  markerad = false,
}: {
  namn: string;
  belopp: string;
  enhet: string;
  punkter: string[];
  markerad?: boolean;
}) {
  return (
    <div
      className={`flex flex-col rounded border bg-kort p-6 ${
        markerad ? "border-2 border-signal" : "border-linje"
      }`}
    >
      <h3 className="font-semibold">{namn}</h3>
      <p className="mt-2 font-display text-3xl leading-none tracking-tight tabular-nums">
        {belopp}
      </p>
      <p className="mt-1 text-sm text-dimma">{enhet}</p>
      <ul className="mt-5 grid gap-2 text-sm">
        {punkter.map((p) => (
          <li key={p} className="grid grid-cols-[auto_1fr] gap-2">
            <span aria-hidden="true" className="text-signal">
              →
            </span>
            {p}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Punkt({
  rubrik,
  children,
}: {
  rubrik: string;
  children: React.ReactNode;
}) {
  return (
    <li className="grid grid-cols-[auto_1fr] gap-4">
      <span
        aria-hidden="true"
        className="mt-1 grid h-6 w-6 flex-none place-items-center rounded-full bg-larm-svag text-sm font-bold text-larm"
      >
        ×
      </span>
      <div>
        <h3 className="font-semibold">{rubrik}</h3>
        <p className="mt-1 text-dimma">{children}</p>
      </div>
    </li>
  );
}
