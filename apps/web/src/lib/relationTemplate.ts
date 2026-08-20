import katex from "katex";

import type { RelationOut } from "./types";

// {in0}, {in1}, {out0}: an operand's position in the relation, not its identity.
const PLACEHOLDER = /\{(in|out)(\d+)\}/g;
const OBJECT_HREF = /^\/objects\/([0-9a-fA-F-]{36})$/;

export const objectHrefMatch = (href: string | null | undefined): string | null =>
  OBJECT_HREF.exec(href ?? "")?.[1] ?? null;

// Whether a piece of object LaTeX survives KaTeX on its own. One unparseable operand turns the
// whole substituted expression into red error text, so each is checked before it goes in, and a
// bad one sends the row to the plain fallback layout instead. Keyed by the latex itself, so
// editing an object produces a new key rather than a stale hit.
const renderable = new Map<string, boolean>();

function isRenderable(latex: string): boolean {
  const cached = renderable.get(latex);
  if (cached !== undefined) return cached;
  let ok = true;
  try {
    katex.renderToString(latex, { throwOnError: true, output: "html" });
  } catch {
    ok = false;
  }
  renderable.set(latex, ok);
  return ok;
}

/**
 * Render `template` with its placeholders replaced by this relation's operands, or return null
 * when the template cannot faithfully represent this relation — the caller then falls back to
 * the plain operands-operator-outputs row.
 *
 * Substitution happens in the LaTeX source and the result is typeset in one pass, rather than
 * splitting the template on placeholders and typesetting the pieces. Splitting cannot express
 * a placeholder inside a group at all (`\frac{{in0}}{{in1}}` would hand KaTeX the fragment
 * `\frac{`), and it also loses spacing: a lone " + " typesets as an ordinary symbol rather than
 * a binary operator, so `A + B = E` would come out jammed together.
 *
 * Operands stay individually clickable because each is wrapped in \href, which KaTeX emits as a
 * real anchor inside the layout — so cmd-click and "copy link address" work as they should.
 */
export function buildTemplateHtml(template: string, relation: RelationOut): string | null {
  const allowedHrefs = new Set<string>();
  const covered = new Set<string>();
  // A list rather than a boolean: TypeScript does not track assignments made inside the
  // replacer closure, so a flag would read as permanently false to the type checker.
  const unusable: string[] = [];

  // A function replacer, never a string one: a string replacement would interpret $& and $1
  // appearing inside an operand's LaTeX.
  const source = template.replace(PLACEHOLDER, (_match, kind: string, digits: string) => {
    const slots = kind === "in" ? relation.inputs : relation.outputs;
    const slot = slots.at(Number(digits));
    if (slot === undefined || !isRenderable(slot.object.latex)) {
      unusable.push(`${kind}${digits}`);
      return "";
    }
    const href = `/objects/${slot.object.id}`;
    allowedHrefs.add(href);
    covered.add(`${kind}${digits}`);
    return `\\href{${href}}{${slot.object.latex}}`;
  });

  if (unusable.length > 0) return null;
  // Every operand has to appear at least once. Repeats are fine and useful ({in0} \cdot {in0});
  // omissions are not, because a template belongs to the operator while arity belongs to the
  // relation — so Add(A, B, C) under "{in0} + {in1} = {out0}" would render a false equation.
  if (covered.size !== relation.inputs.length + relation.outputs.length) return null;

  try {
    return katex
      .renderToString(source, {
        // Unlike Latex.tsx, which has nowhere else to go: here a correct fallback exists, so
        // failing loudly and taking it beats rendering red error text.
        throwOnError: true,
        displayMode: false,
        // MathML is dropped so the anchors below aren't buried inside the aria-hidden copy
        // KaTeX wraps its visual output in — a focusable link no screen reader can reach is
        // the worse trade. Screen readers then read the glyph run in DOM order.
        output: "html",
        // NEVER `trust: true`. Object LaTeX is user input, and blanket trust would enable
        // \href{javascript:...}, \includegraphics and \htmlStyle from anything typed into the
        // latex field. Only the relative object links built just above are allowed through.
        trust: (context) =>
          context.command === "\\href" &&
          context.protocol === "_relative" &&
          allowedHrefs.has(context.url),
      })
      .replace(' aria-hidden="true"', "");
  } catch {
    return null;
  }
}
