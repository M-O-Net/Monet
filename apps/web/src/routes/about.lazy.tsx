import { createLazyFileRoute, Link } from "@tanstack/react-router";
import Markdown, { type Components } from "react-markdown";

import prd from "../../../../docs/PRD.md?raw";

export const Route = createLazyFileRoute("/about")({
  component: AboutPage,
});

const PROSE: Components = {
  h1: ({ children }) => <h1 className="mb-4 font-display text-2xl text-ink">{children}</h1>,
  h2: ({ children }) => (
    <h2 className="mt-10 mb-3 border-b border-mist pb-1 font-display text-xl text-ink">
      {children}
    </h2>
  ),
  h3: ({ children }) => <h3 className="mt-6 mb-2 font-display text-lg text-ink">{children}</h3>,
  p: ({ children }) => <p className="mb-3 text-sm leading-relaxed text-ink">{children}</p>,
  ul: ({ children }) => (
    <ul className="mb-3 list-disc space-y-1 pl-5 text-sm leading-relaxed text-ink">{children}</ul>
  ),
  li: ({ children }) => <li className="[&>ul]:mt-1 [&>ul]:mb-1">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-ink">{children}</strong>,
  a: ({ children, href }) => (
    <a href={href} className="text-pond underline underline-offset-2">
      {children}
    </a>
  ),
};

function AboutPage() {
  return (
    <article className="max-w-3xl">
      <p className="mb-6 text-xs text-ink-soft">
        How big is the database?{" "}
        <Link to="/storage" className="text-pond underline underline-offset-2">
          See its storage
        </Link>
        .
      </p>
      <Markdown components={PROSE}>{prd}</Markdown>
    </article>
  );
}
