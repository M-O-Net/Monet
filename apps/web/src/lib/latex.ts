/**
 * Whitespace-insensitive comparison key for LaTeX, mirroring `normalize_latex` in
 * apps/api/src/monet_api/objects/service.py.
 *
 * Duplicated rather than shared because it's needed in two runtimes; the copy here only labels
 * a preview ("new" vs "already in the network"), while the API's copy is what actually decides
 * whether an object is created. If they ever disagree the server still wins — the preview label
 * is the only thing that would look wrong.
 */
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
