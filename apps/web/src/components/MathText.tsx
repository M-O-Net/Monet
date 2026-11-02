import { Fragment, useMemo } from "react";

import { splitMath } from "../lib/mathText";
import { Latex } from "./Latex";

export function MathText({ children }: { children: string }) {
  const segments = useMemo(() => splitMath(children), [children]);
  return (
    <>
      {segments.map((segment, index) =>
        segment.kind === "text" ? (
          <Fragment key={index}>{segment.value}</Fragment>
        ) : (
          <Latex key={index} display={segment.kind === "display"}>
            {segment.value}
          </Latex>
        ),
      )}
    </>
  );
}
