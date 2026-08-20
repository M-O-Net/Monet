const TEXT_GROUP = /\\text\{[^{}]*\}/g;

export function normalizeLatex(latex: string): string {
  const parts: string[] = [];
  let last = 0;
  for (const match of latex.matchAll(TEXT_GROUP)) {
    parts.push(latex.slice(last, match.index).replace(/\s+/g, ""));
    parts.push(match[0].replace(/\s+/g, " "));
    last = match.index + match[0].length;
  }
  parts.push(latex.slice(last).replace(/\s+/g, ""));
  return parts.join("");
}
