import { useNavigate } from "@tanstack/react-router";

import { objectHrefMatch } from "../../lib/relationTemplate";

export function RelationExpression({ html }: { html: string }) {
  const navigate = useNavigate();

  return (
    <span
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
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
