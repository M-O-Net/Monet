import katex from "katex";

import type { RelationOut } from "./types";

// {in0}, {in1}, {out0}: an operand's position in the relation, not its identity.
const PLACEHOLDER = /\{(in|out)(\d+)\}/g;
const OBJECT_HREF = /^\/objects\/([0-9a-fA-F-]{36})$/;

// Marks the object whose page is being viewed, wherever it turns up in a formula.
const CURRENT_CLASS = "is-current";

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
 *
 * A template marks its own operator notation with \op{...}: "{in0} \op{+} {in1} = {out0}" makes
 * the plus a link to Matrix Addition, which is what the plus denotes. It is a KaTeX macro that
 * expands to the same \href, so the operator comes out as an ordinary anchor — styled, placed
 * and click-handled exactly like an operand, with no special-casing anywhere downstream.
 */
export function buildTemplateHtml(
  template: string,
  relation: RelationOut,
  {
    strict = true,
    currentObjectId = null,
  }: { strict?: boolean; currentObjectId?: string | null } = {},
): string | null {
  const operatorIsCurrent = relation.operator.id === currentObjectId;
  const operatorHref = `/objects/${relation.operator.id}`;
  const allowedHrefs = new Set<string>(operatorIsCurrent ? [] : [operatorHref]);

  // The object whose page this is gets marked, not linked: it is already here, so a link would
  // lead back to where you are.
  const reference = (id: string, latex: string) =>
    id === currentObjectId
      ? `\\htmlClass{${CURRENT_CLASS}}{${latex}}`
      : `\\href{/objects/${id}}{${latex}}`;
  const covered = new Set<string>();
  // A list rather than a boolean: TypeScript does not track assignments made inside the
  // replacer closure, so a flag would read as permanently false to the type checker.
  const unusable: string[] = [];

  // A function replacer, never a string one: a string replacement would interpret $& and $1
  // appearing inside an operand's LaTeX.
  const source = template.replace(PLACEHOLDER, (_match, kind: string, digits: string) => {
    const slots = kind === "in" ? relation.inputs : relation.outputs;
    const slot = slots.at(Number(digits));
    if (slot === undefined || (strict && !isRenderable(slot.object.latex))) {
      unusable.push(`${kind}${digits}`);
      return "";
    }
    allowedHrefs.add(`/objects/${slot.object.id}`);
    covered.add(`${kind}${digits}`);
    return reference(slot.object.id, slot.object.latex);
  });

  if (unusable.length > 0) return null;
  // Every operand has to appear at least once. Repeats are fine and useful ({in0} \cdot {in0});
  // omissions are not, because a template belongs to the operator while arity belongs to the
  // relation — so Add(A, B, C) under "{in0} + {in1} = {out0}" would render a false equation.
  if (strict && covered.size !== relation.inputs.length + relation.outputs.length) return null;

  try {
    return katex
      .renderToString(source, {
        // Strict only. An author's template has somewhere to fall back to, so failing loudly
        // and taking it beats rendering red error text; the default template below has not, and
        // cannot state anything false either way, so it shows a bad operand as a bad operand.
        throwOnError: strict,
        displayMode: false,
        // MathML is dropped so the anchors below aren't buried inside the aria-hidden copy
        // KaTeX wraps its visual output in — a focusable link no screen reader can reach is
        // the worse trade. Screen readers then read the glyph run in DOM order.
        output: "html",
        // \op{...} is how a template says "this notation is the operator itself".
        macros: {
          "\\op": operatorIsCurrent
            ? `\\htmlClass{${CURRENT_CLASS}}{#1}`
            : `\\href{${operatorHref}}{#1}`,
        },
        // \htmlClass sits behind KaTeX's htmlExtension warning, which does not apply when the
        // only class that can reach it is the one written just above.
        strict: (code: string) => (code === "htmlExtension" ? "ignore" : "warn"),
        // NEVER `trust: true`. Object LaTeX is user input, and blanket trust would enable
        // \href{javascript:...}, \includegraphics and \htmlStyle from anything typed into the
        // latex field. Only the relative object links built just above are allowed through.
        trust: (context) =>
          (context.command === "\\href" &&
            context.protocol === "_relative" &&
            allowedHrefs.has(context.url)) ||
          (context.command === "\\htmlClass" && context.class === CURRENT_CLASS),
      })
      .replace(' aria-hidden="true"', "");
  } catch {
    return null;
  }
}

/**
 * The template used when an operator has not asked for one: the operands, an arrow, the results.
 *
 * Generated per relation rather than fixed, since arity belongs to the relation. Going through
 * the same typesetting as any other template is what keeps the arrow on the same baseline as
 * the mathematics either side of it — drawn out of box-characters it never quite lined up.
 */
function defaultTemplate(relation: RelationOut): string {
  const operands = (kind: string, count: number) =>
    Array.from({ length: count }, (_slot, i) => `{${kind}${String(i)}}`).join(",\\;");
  return [
    operands("in", relation.inputs.length),
    "\\op{\\longrightarrow}",
    operands("out", relation.outputs.length),
  ].join(" ");
}

/**
 * How a relation reads: the operator's own template when it has one and that template can
 * represent this relation, and the plain operands-arrow-results form otherwise.
 *
 * Always returns markup, so a row is never blank. The default form is rendered leniently
 * because it has nowhere left to fall back to, and unlike an author's template it cannot say
 * anything untrue — an operand whose latex will not parse simply shows up unparsed.
 */
export function buildRelationHtml(
  relation: RelationOut,
  template: string | null,
  currentObjectId: string | null,
): string {
  const authored =
    template === null ? null : buildTemplateHtml(template, relation, { currentObjectId });
  return (
    authored ??
    buildTemplateHtml(defaultTemplate(relation), relation, { strict: false, currentObjectId }) ??
    ""
  );
}
