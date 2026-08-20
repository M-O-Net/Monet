import { useNavigate } from "@tanstack/react-router";

import { objectHrefMatch } from "../../lib/relationTemplate";

/**
 * A relation as one typeset expression.
 *
 * Every clickable part is a real anchor KaTeX put in the layout — the operands, and whatever
 * notation the template marked with \op{...}, which is the operator itself. They are not React
 * elements and cannot carry an onClick each, so one delegated handler turns a plain left-click
 * into a client-side navigation and leaves modified and middle clicks to the browser, which the
 * hrefs already describe correctly. Hover is delegated too, a level further up on the row.
 */
export function RelationExpression({ html }: { html: string }) {
  const navigate = useNavigate();

  return (
    <span
      // Anchor styling lives in index.css under this class. As stacked arbitrary variants
      // (`[&_a]:border` and friends) the declarations compiled to rules of equal specificity,
      // and the border-width utility's own `currentColor` kept winning the tie, outlining every
      // operand in ink at rest.
      className="relation-formula"
      onClick={(event) => {
        if (event.defaultPrevented || event.button !== 0) return;
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const anchor = (event.target as HTMLElement).closest("a");
        const objectId = objectHrefMatch(anchor?.getAttribute("href"));
        if (objectId === null) return;
        event.preventDefault();
        void navigate({ to: "/objects/$objectId", params: { objectId } });
      }}
      // Safe only because buildRelationHtml is the sole producer of this string: it is KaTeX
      // output, and its trust predicate allows nothing but the object links it built itself.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
