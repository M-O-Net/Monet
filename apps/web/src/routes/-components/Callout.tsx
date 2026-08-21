import type { ReactNode } from "react";

export function Callout({
  heading,
  children,
  tone = "gold",
}: {
  heading: string;
  children: ReactNode;
  tone?: "gold" | "pond";
}) {
  const accent = tone === "pond" ? "border-l-pond bg-pond/5" : "border-l-gold bg-gold-soft/30";
  return (
    <section
      className={`mt-6 mb-7 rounded-sm border border-mist border-l-2 px-4 py-3 ${accent} shadow-[0_1px_3px_rgba(35,50,43,0.06)]`}
    >
      <h2 className="mb-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">
        {heading}
      </h2>
      {children}
    </section>
  );
}
