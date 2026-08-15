import katex from "katex";
import { useMemo } from "react";

export function Latex({ children }: { children: string }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(children, { throwOnError: false, displayMode: false });
    } catch {
      return children;
    }
  }, [children]);

  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
