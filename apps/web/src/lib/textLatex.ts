const TEXT_MODE_ESCAPES: Record<string, string> = {
  "\\": "\\textbackslash{}",
  "{": "\\{",
  "}": "\\}",
  "#": "\\#",
  $: "\\$",
  "%": "\\%",
  "&": "\\&",
  _: "\\_",
  "^": "\\textasciicircum{}",
  "~": "\\textasciitilde{}",
};

export function textLatex(name: string): string {
  const escaped = name
    .trim()
    .replace(/[\\{}#$%&_^~]/g, (character) => TEXT_MODE_ESCAPES[character] ?? character);
  return `\\text{${escaped}}`;
}
