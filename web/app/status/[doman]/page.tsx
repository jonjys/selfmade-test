import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ALLVARLIGHET_SV,
  allaKunder,
  hämtaKund,
  riktning,
  type Kund,
} from "@/lib/data";
import Trendkurva from "./Trendkurva";

export function generateStaticParams() {
  return allaKunder().map((k) => ({ doman: k.doman }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ doman: string }>;
}) {
  const { doman } = await params;
  const kund = hämtaKund(doman);
  return { title: kund ? `Tillgänglighet: ${kund.namn}` : "Okänd sajt" };
}

export default async function Status({
  params,
}: {
  params: Promise<{ doman: string }>;
}) {
  const { doman } = await params;
  const kund = hämtaKund(doman);
  if (!kund) notFound();

  const r = riktning(kund);

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-dimma">
        ← Tillbaka
      </Link>

      <header className="mt-6 border-b-[3px] border-signal pb-6">
        <p className="text-xs font-bold uppercase tracking-[0.17em] text-signal">
          Status
        </p>
        <h1 className="mt-2 font-display text-4xl font-semibold tracking-tight">
          {kund.namn}
        </h1>
        <p className="mt-2 text-sm text-dimma">
          Senast skannad {kund.senastSkannad} · WCAG 2.1 AA
        </p>
      </header>

      <Riktningsbesked kund={kund} status={r.status} skillnad={r.skillnad} />

      <dl className="mt-8 grid gap-px overflow-hidden rounded border border-linje bg-linje sm:grid-cols-3">
        <Ruta
          tal={kund.allvarliga}
          text="allvarliga eller kritiska"
          varning={kund.allvarliga > 0}
        />
        <Ruta tal={kund.totalt} text="element totalt" />
        <Ruta tal={kund.brister.length} text="olika typer av brist" />
      </dl>

      {kund.historik.length > 1 && (
        <section className="mt-12">
          <h2 className="font-display text-2xl font-semibold tracking-tight">
            Utveckling
          </h2>
          <p className="mt-1 text-sm text-dimma">
            Antal element som bryter mot kraven, per skanning.
          </p>
          <Trendkurva punkter={kund.historik} />
        </section>
      )}

      <section className="mt-12">
        <h2 className="font-display text-2xl font-semibold tracking-tight">
          Brister just nu
        </h2>
        <p className="mt-1 text-sm text-dimma">
          Sorterade efter allvarlighetsgrad. Åtgärda uppifrån.
        </p>
        <ul className="mt-6 grid gap-3">
          {kund.brister.map((b) => (
            <li
              key={b.regelId}
              className={`rounded border border-l-[3px] border-linje bg-kort p-5 ${
                b.allvarlighet === "critical" || b.allvarlighet === "serious"
                  ? "border-l-larm"
                  : "border-l-dimma"
              }`}
            >
              <div className="flex flex-wrap items-baseline gap-3">
                <h3 className="font-semibold">{b.rubrik}</h3>
                <span className="rounded border border-current px-2 py-0.5 text-[0.65rem] font-bold uppercase tracking-wider text-larm">
                  {ALLVARLIGHET_SV[b.allvarlighet]}
                </span>
                {kund.nya.includes(b.regelId) && (
                  <span className="rounded bg-larm-svag px-2 py-0.5 text-[0.65rem] font-bold uppercase tracking-wider text-larm">
                    Ny sedan sist
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-dimma">
                {b.antal} element · {b.sidtyp} · WCAG {b.wcag}
              </p>
              <p className="mt-2 text-sm">{b.konsekvens}</p>
            </li>
          ))}
          {kund.brister.length === 0 && (
            <li className="rounded border border-linje bg-kort p-5 text-dimma">
              Den automatiska genomgången hittade inga brister. Det betyder
              inte att sajten är fullt tillgänglig — se avgränsningen nedan.
            </li>
          )}
        </ul>
      </section>

      {kund.lagade.length > 0 && (
        <section className="mt-12 rounded border border-signal bg-signal-svag p-6">
          <h2 className="font-display text-xl font-semibold tracking-tight">
            Åtgärdat sedan förra skanningen
          </h2>
          <ul className="mt-3 grid gap-1 text-sm">
            {kund.lagade.map((id) => (
              <li key={id}>✓ {id}</li>
            ))}
          </ul>
        </section>
      )}

      <aside className="mt-12 rounded border border-l-4 border-fokus bg-papper-djup p-6 text-sm">
        <h2 className="font-semibold">Vad den här sidan inte är</h2>
        <p className="mt-2 text-dimma">
          Siffrorna kommer från en automatisk skanning. Automatiska verktyg
          fångar ungefär en tredjedel av alla tillgänglighetsbrister — resten
          kräver manuell testning med skärmläsare och tangentbord. Det
          verkliga antalet ligger sannolikt närmare{" "}
          <b>{Math.round(kund.totalt / 0.35)} element</b>.
        </p>
        <p className="mt-2 text-dimma">
          Sidan är inte ett juridiskt utlåtande och innebär inte att sajten
          uppfyller eller inte uppfyller lagens krav.
        </p>
      </aside>
    </div>
  );
}

function Riktningsbesked({
  kund,
  status,
  skillnad,
}: {
  kund: Kund;
  status: ReturnType<typeof riktning>["status"];
  skillnad: number;
}) {
  if (status === "första") {
    return (
      <p className="mt-8 rounded border border-linje bg-kort p-5">
        Första skanningen är gjord. Nästa vecka kan vi visa riktningen.
      </p>
    );
  }
  if (status === "sämre") {
    return (
      <p className="mt-8 rounded border border-larm bg-larm-svag p-5">
        <b>{skillnad} fler element</b> bryter mot kraven än vid förra
        skanningen. Det brukar betyda att en ny release återinfört något som
        tidigare var åtgärdat.
      </p>
    );
  }
  if (status === "bättre") {
    return (
      <p className="mt-8 rounded border border-signal bg-signal-svag p-5">
        <b>{Math.abs(skillnad)} färre element</b> bryter mot kraven än vid
        förra skanningen. {kund.allvarliga > 0 ? "Fortsätt uppifrån i listan." : ""}
      </p>
    );
  }
  return (
    <p className="mt-8 rounded border border-linje bg-kort p-5 text-dimma">
      Oförändrat sedan förra skanningen.
    </p>
  );
}

function Ruta({
  tal,
  text,
  varning = false,
}: {
  tal: number;
  text: string;
  varning?: boolean;
}) {
  return (
    <div className="bg-kort px-5 py-6">
      <dt className="sr-only">{text}</dt>
      <dd>
        <span
          className={`block font-display text-4xl leading-none tracking-tight tabular-nums ${
            varning ? "text-larm" : ""
          }`}
        >
          {tal}
        </span>
        <span className="mt-2 block text-sm text-dimma">{text}</span>
      </dd>
    </div>
  );
}
