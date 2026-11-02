import katex from "katex";
import { useMemo } from "react";

export function Latex({ children, display = false }: { children: string; display?: boolean }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(children, { throwOnError: false, displayMode: display });
    } catch {
      return children;
    }
  }, [children, display]);

  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}
