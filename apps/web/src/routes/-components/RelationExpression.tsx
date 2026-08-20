import { useNavigate } from "@tanstack/react-router";
import { useMemo } from "react";

import { buildTemplateHtml, objectHrefMatch } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";

/**
 * A relation rendered through its operator's template, as one typeset expression.
 *
 * Every visible part of the expression points at the object it denotes. The operands are real
 * anchors that KaTeX put inside the layout — not React elements, so they cannot carry an onClick
 * each — and everything else is the operator's own notation: the "+" in `A + B = E` *is* Matrix
 * Addition, so clicking it goes to Matrix Addition, the same as clicking the badge does in the
 * plain layout. One delegated handler covers both cases, and leaves modified and middle clicks
 * to the browser so the operand hrefs still open in a tab.
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
      // inline-block on the operand anchors: KaTeX lays a matrix out as a tall inline-block
      // inside an inline <a>, and an inline box is only as tall as its own line box — so a
      // hover background painted a thin band through the middle of the matrix instead of
      // covering it. Shrink-wrapping the anchor makes the highlight match what you are pointing
      // at, and measures identically for spacing and baseline.
      className="cursor-pointer [&_a]:inline-block [&_a]:rounded-sm [&_a]:text-ink [&_a]:no-underline [&_a:hover]:bg-gold-soft/60"
      title={`Applying ${relation.operator.latex.replace(/^\\text\{(.*)\}$/, "$1")}`}
      onClick={(event) => {
        if (event.defaultPrevented || event.button !== 0) return;
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const anchor = (event.target as HTMLElement).closest("a");
        const objectId = objectHrefMatch(anchor?.getAttribute("href"));
        event.preventDefault();
        void navigate({
          to: "/objects/$objectId",
          // Not an operand, so the click landed on the operator's own notation.
          params: { objectId: objectId ?? relation.operator.id },
        });
      }}
      // Safe only because buildTemplateHtml is the sole producer of this string: it is KaTeX
      // output, and its trust predicate allows nothing but the object links it built itself.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
