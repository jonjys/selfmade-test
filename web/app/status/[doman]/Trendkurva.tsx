import type { Mätpunkt } from "@/lib/data";

/**
 * Utvecklingen över tid.
 *
 * Diagrammet är dekoration för den som ser det, och därför aria-hidden.
 * Samma data ligger som en riktig tabell under, synlig för alla — inte gömd
 * bakom en visually-hidden-klass, eftersom en tabell med fyra rader är
 * användbar för seende också.
 *
 * Ett tillgänglighetsföretag som levererar ett otillgängligt diagram har
 * ingen produkt att sälja.
 */
export default function Trendkurva({ punkter }: { punkter: Mätpunkt[] }) {
  const bredd = 640;
  const höjd = 160;
  const marginal = 12;

  const max = Math.max(...punkter.map((p) => p.totalt), 1);
  const steg =
    punkter.length > 1 ? (bredd - marginal * 2) / (punkter.length - 1) : 0;

  const koordinater = punkter.map((p, i) => {
    const x = marginal + i * steg;
    const y = höjd - marginal - (p.totalt / max) * (höjd - marginal * 2);
    return { x, y, ...p };
  });

  const linje = koordinater.map((k) => `${k.x},${k.y}`).join(" ");
  const yta = `${marginal},${höjd - marginal} ${linje} ${
    koordinater[koordinater.length - 1].x
  },${höjd - marginal}`;

  const sista = koordinater[koordinater.length - 1];

  return (
    <figure className="mt-6">
      <svg
        viewBox={`0 0 ${bredd} ${höjd}`}
        className="w-full rounded border border-linje bg-kort"
        aria-hidden="true"
        focusable="false"
      >
        <polygon points={yta} fill="var(--color-signal)" opacity="0.08" />
        <polyline
          points={linje}
          fill="none"
          stroke="var(--color-signal)"
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {/* Sista punkten markeras, eftersom det är den som gäller nu. */}
        <circle
          cx={sista.x}
          cy={sista.y}
          r="5"
          fill="var(--color-kort)"
          stroke="var(--color-signal)"
          strokeWidth="2.5"
        />
      </svg>

      <figcaption className="sr-only">
        Antal element som bryter mot kraven per skanning. Samma siffror finns i
        tabellen nedan.
      </figcaption>

      <table className="mt-4 w-full text-sm">
        <caption className="sr-only">
          Antal element som bryter mot kraven per skanning
        </caption>
        <thead>
          <tr className="border-b border-linje text-xs uppercase tracking-wider text-dimma">
            <th scope="col" className="py-2 text-left font-medium">
              Datum
            </th>
            <th scope="col" className="py-2 text-right font-medium">
              Totalt
            </th>
            <th scope="col" className="py-2 text-right font-medium">
              Allvarliga
            </th>
          </tr>
        </thead>
        <tbody>
          {[...punkter].reverse().map((p) => (
            <tr key={p.datum} className="border-b border-linje">
              <td className="py-2">{p.datum}</td>
              <td className="py-2 text-right tabular-nums">{p.totalt}</td>
              <td className="py-2 text-right tabular-nums">{p.allvarliga}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
