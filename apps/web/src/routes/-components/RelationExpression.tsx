import { useNavigate } from "@tanstack/react-router";
import { useMemo } from "react";

import { buildTemplateHtml, objectHrefMatch } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";

/**
 * A relation rendered through its operator's template, as one typeset expression.
 *
 * Every clickable part is a real anchor KaTeX put in the layout — the operands, and whatever
 * notation the template marked with \op{...}, which is the operator itself. They are not React
 * elements and cannot carry an onClick each, so one delegated handler turns a plain left-click
 * into a client-side navigation and leaves modified and middle clicks to the browser, which the
 * hrefs already describe correctly.
 */
export function RelationExpression({
  relation,
  template,
}: {
  relation: RelationOut;
  template: string;
}) {
  const navigate = useNavigate();
  const html = useMemo(() => buildTemplateHtml(template, relation), [template, relation]);

  if (html === null) return null;

  return (
    <span
      // inline-block on the anchors: KaTeX lays a matrix out as a tall inline-block, and raises
      // a superscript inside its own box — so an inline anchor around either is only as tall as
      // its line box, and the hover highlight landed as a thin band through the middle of a
      // matrix, or below the "-1" it belonged to. Shrink-wrapping puts the highlight on the
      // glyph it belongs to, and measures identically for position and baseline.
      className="[&_a]:inline-block [&_a]:cursor-pointer [&_a]:rounded-sm [&_a]:text-ink [&_a]:no-underline [&_a:hover]:bg-gold-soft/60"
      onClick={(event) => {
        if (event.defaultPrevented || event.button !== 0) return;
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const anchor = (event.target as HTMLElement).closest("a");
        const objectId = objectHrefMatch(anchor?.getAttribute("href"));
        if (objectId === null) return;
        event.preventDefault();
        void navigate({ to: "/objects/$objectId", params: { objectId } });
      }}
      // Safe only because buildTemplateHtml is the sole producer of this string: it is KaTeX
      // output, and its trust predicate allows nothing but the object links it built itself.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
