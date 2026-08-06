"use client";

import { useId, useState } from "react";
import {
  MOTTAGARE,
  ÄR_KONFIGURERAD,
  mejllänk,
  serUtSomDomän,
  städaDomän,
} from "@/lib/kontakt";

/**
 * Vägen från besökare till förfrågan.
 *
 * Ingen server tar emot den. Formuläret öppnar besökarens egen e-postklient
 * med allt ifyllt — fulare än ett backend-anrop, men det fungerar från första
 * minuten, kan inte gå sönder klockan tre på natten, och besökaren ser exakt
 * vad som skickas. Det bygger mer förtroende än ett formulär som sväljer
 * uppgifterna utan kvittens.
 *
 * Adressen visas dessutom som en vanlig länk. En del skriver hellre själva,
 * och en sida som bara går att kontakta via ett formulär stänger ute den som
 * har ett mejlprogram som inte svarar på mailto.
 */
export default function Skanforfragan() {
  const [värde, setVärde] = useState("");
  const [fel, setFel] = useState<string | null>(null);
  const [kvitto, setKvitto] = useState<string | null>(null);

  const fältId = useId();
  const hjälpId = `${fältId}-hjalp`;
  const felId = `${fältId}-fel`;

  function skicka(e: React.FormEvent) {
    e.preventDefault();
    const domän = städaDomän(värde);

    if (!domän) {
      setFel("Fyll i adressen till butiken, till exempel butiken.se");
      setKvitto(null);
      return;
    }
    if (!serUtSomDomän(värde)) {
      setFel(`”${värde.trim()}” ser inte ut som en webbadress. Prova butiken.se`);
      setKvitto(null);
      return;
    }
    setFel(null);

    if (!ÄR_KONFIGURERAD) {
      setKvitto(
        "Sidan är inte färdigkonfigurerad — mottagaradressen är inte satt " +
          "än. Sätt NEXT_PUBLIC_MOTTAGARE eller byt adressen i " +
          "web/lib/kontakt.ts.",
      );
      return;
    }

    window.location.href = mejllänk(domän);
    setKvitto(
      `Ert e-postprogram öppnas med en förfrågan om ${domän}. ` +
        `Händer ingenting, mejla ${MOTTAGARE} direkt.`,
    );
  }

  return (
    <section
      id="skanning"
      className="scroll-mt-8 border-b border-linje px-6 py-16"
    >
      <div className="mx-auto max-w-2xl">
        <p className="mb-5 flex items-center gap-3 text-xs font-bold uppercase tracking-[0.17em] text-signal">
          Kostnadsfritt
          <span aria-hidden="true" className="h-px flex-1 bg-linje" />
        </p>
        <h2 className="font-display text-3xl font-semibold tracking-tight text-balance">
          Se vad en skanning hittar hos er
        </h2>
        <p className="mt-4 max-w-xl text-dimma">
          Vi går igenom startsida, produktsida och kassa och skickar de tre
          allvarligaste bristerna med skärmbild. Inget konto, ingen bindning,
          svar inom ett dygn.
        </p>

        <form onSubmit={skicka} noValidate className="mt-8">
          <label htmlFor={fältId} className="block font-semibold">
            Adressen till er butik
          </label>
          <p id={hjälpId} className="mt-1 text-sm text-dimma">
            Till exempel <code>butiken.se</code>. Både med och utan https://
            fungerar.
          </p>

          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <input
              id={fältId}
              name="domän"
              type="text"
              inputMode="url"
              autoComplete="url"
              spellCheck={false}
              value={värde}
              onChange={(e) => setVärde(e.target.value)}
              aria-describedby={fel ? `${hjälpId} ${felId}` : hjälpId}
              aria-invalid={fel ? true : undefined}
              placeholder="butiken.se"
              className={`w-full flex-1 rounded border bg-kort px-4 py-3 text-base ${
                fel ? "border-larm" : "border-linje"
              }`}
            />
            <button
              type="submit"
              className="rounded border-2 border-signal bg-signal px-6 py-3 font-semibold text-papper transition-opacity hover:opacity-90 sm:flex-none"
            >
              Begär skanning
            </button>
          </div>

          {/* Felet måste läsas upp när det dyker upp, inte bara synas. */}
          <p id={felId} role="alert" className="mt-3 text-sm text-larm">
            {fel}
          </p>

          {/* role="status" är artigt: det avbryter inte den som skriver. */}
          <p role="status" className="mt-1 text-sm text-dimma">
            {kvitto}
          </p>
        </form>

        <p className="mt-6 text-sm text-dimma">
          {ÄR_KONFIGURERAD ? (
            <>
              Skriver ni hellre själva:{" "}
              <a href={`mailto:${MOTTAGARE}`} className="text-signal underline">
                {MOTTAGARE}
              </a>
            </>
          ) : (
            <>Kontaktadressen är inte satt än.</>
          )}
        </p>
      </div>
    </section>
  );
}
