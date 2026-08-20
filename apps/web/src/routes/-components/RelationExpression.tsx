import { useNavigate } from "@tanstack/react-router";
import { useMemo } from "react";

import { buildTemplateHtml, objectHrefMatch } from "../../lib/relationTemplate";
import type { RelationOut } from "../../lib/types";

/**
 * A relation rendered through its operator's template, as one typeset expression.
 *
 * The operand links are real anchors that KaTeX put inside the layout, so they are not React
 * elements and cannot carry an onClick each. One delegated handler on the wrapper turns a plain
 * left-click into a client-side navigation and leaves every other click alone, so cmd-click and
 * middle-click still open a tab the way the href promises.
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
      className="[&_a]:cursor-pointer [&_a]:rounded-sm [&_a]:text-ink [&_a]:no-underline [&_a:hover]:bg-gold-soft/60"
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
