"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Sidans tes, som interaktion.
 *
 * Besökaren tabbar genom en kassa och ser fokusringen. Slår de av vippan
 * ligger fokus kvar men syns inte längre — vilket är precis vad en enda
 * CSS-rad gör med en riktig butik. Argumentet behöver inte förklaras, det
 * går att känna.
 */
export default function FokusDemo() {
  const [markering, setMarkering] = useState(true);
  const [status, setStatus] = useState<string | null>(null);
  const [pekskarm, setPekskarm] = useState(false);
  const ram = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // "Tryck Tab" är omöjligt att följa på en telefon, och skulle få demot
    // att se trasigt ut i stället för att förklara något.
    setPekskarm(window.matchMedia("(hover: none)").matches);
  }, []);

  function namnge(el: EventTarget | null): string | null {
    if (!(el instanceof HTMLElement)) return null;
    if (el.id === "vippa") return "vippan för fokusmarkering";
    const etikett = (el as HTMLInputElement).labels?.[0];
    if (etikett) return `fältet ${etikett.textContent?.trim().toLowerCase()}`;
    if (el.tagName === "BUTTON")
      return `knappen ${el.textContent?.trim().toLowerCase()}`;
    return null;
  }

  const instruktion = pekskarm
    ? "Tryck i ett fält nedan så ser du markeringen."
    : "Tryck Tab för att flytta dig genom kassan.";

  const vilostatus = pekskarm
    ? "Ingen markering ännu — tryck i ett fält."
    : "Ingen markering ännu — tryck Tab.";

  return (
    <div
      ref={ram}
      className={`mt-10 overflow-hidden rounded border border-linje bg-kort ${
        markering ? "" : "[&_:focus]:outline-none [&_:focus-visible]:outline-none"
      }`}
      onFocus={(e) => {
        const namn = namnge(e.target);
        if (namn) setStatus(namn);
      }}
      onBlur={(e) => {
        if (!ram.current?.contains(e.relatedTarget as Node)) setStatus(null);
      }}
    >
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-linje bg-papper-djup px-5 py-3 text-sm">
        <p>
          <span className="font-semibold">Prova själv.</span>{" "}
          <span className="text-dimma">{instruktion}</span>
        </p>
        <label className="flex cursor-pointer items-center gap-2">
          <input
            id="vippa"
            type="checkbox"
            checked={markering}
            onChange={(e) => setMarkering(e.target.checked)}
            className="peer sr-only"
          />
          <span
            aria-hidden="true"
            className="relative h-[22px] w-10 flex-none rounded-full border border-linje bg-larm transition-colors peer-checked:bg-signal after:absolute after:left-0.5 after:top-0.5 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition-transform peer-checked:after:translate-x-[18px] peer-focus-visible:outline peer-focus-visible:outline-[3px] peer-focus-visible:outline-offset-[3px] peer-focus-visible:outline-fokus"
          />
          <span>Fokusmarkering</span>
        </label>
      </div>

      <form className="px-5 py-6" onSubmit={(e) => e.preventDefault()}>
        <div className="grid gap-4 sm:grid-cols-2">
          <Falt id="d-namn" etikett="Namn" standard="Anna Lind" />
          <Falt id="d-post" etikett="Postnummer" standard="118 25" />
        </div>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <label
              htmlFor="d-frakt"
              className="mb-1 block text-xs font-semibold uppercase tracking-wider text-dimma"
            >
              Leveranssätt
            </label>
            <select
              id="d-frakt"
              className="w-full rounded border border-linje bg-papper px-3 py-2"
              defaultValue="Ombud, 1–2 dagar"
            >
              <option>Ombud, 1–2 dagar</option>
              <option>Hemleverans, 3 dagar</option>
            </select>
          </div>
          <Falt id="d-kod" etikett="Rabattkod" standard="" />
        </div>
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            className="rounded border border-linje px-5 py-2 font-semibold"
          >
            Tillbaka
          </button>
          <button
            type="button"
            className="rounded border border-blaeck bg-blaeck px-5 py-2 font-semibold text-papper"
          >
            Slutför köp
          </button>
        </div>
      </form>

      <p
        className="flex min-h-12 items-center gap-2 border-t border-linje bg-papper-djup px-5 py-3 text-sm"
        aria-live="polite"
      >
        <span
          aria-hidden="true"
          className={`h-2 w-2 flex-none rounded-full ${
            status ? (markering ? "bg-signal" : "bg-larm") : "bg-dimma"
          }`}
        />
        {status ? (
          <span>
            Fokus ligger på{" "}
            <code className={markering ? "text-signal" : "text-larm"}>
              {status}
            </code>
            {markering
              ? ". Ringen visar var du är."
              : " — men inget syns."}
          </span>
        ) : (
          <span>{vilostatus}</span>
        )}
      </p>
    </div>
  );
}

function Falt({
  id,
  etikett,
  standard,
}: {
  id: string;
  etikett: string;
  standard: string;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1 block text-xs font-semibold uppercase tracking-wider text-dimma"
      >
        {etikett}
      </label>
      <input
        id={id}
        type="text"
        defaultValue={standard}
        className="w-full rounded border border-linje bg-papper px-3 py-2"
      />
    </div>
  );
}
