import katex from "katex";

import type { RelationOut } from "./types";

const PLACEHOLDER = /\{(in|out)(\d+)\}/g;
const OBJECT_HREF = /^\/objects\/([0-9a-fA-F-]{36})$/;
const CURRENT_CLASS = "is-current";

export const objectHrefMatch = (href: string | null | undefined): string | null =>
  OBJECT_HREF.exec(href ?? "")?.[1] ?? null;

const renderableCache = new Map<string, boolean>();

function rendersOnItsOwn(latex: string): boolean {
  const cached = renderableCache.get(latex);
  if (cached !== undefined) return cached;
  let ok = true;
  try {
    katex.renderToString(latex, { throwOnError: true, output: "html" });
  } catch {
    ok = false;
  }
  renderableCache.set(latex, ok);
  return ok;
}

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

  const reference = (id: string, latex: string) =>
    id === currentObjectId
      ? `\\htmlClass{${CURRENT_CLASS}}{${latex}}`
      : `\\href{/objects/${id}}{${latex}}`;

  const covered = new Set<string>();
  const unrepresentable: string[] = [];

  const source = template.replace(PLACEHOLDER, (_match, kind: string, digits: string) => {
    const slots = kind === "in" ? relation.inputs : relation.outputs;
    const slot = slots.at(Number(digits));
    if (slot === undefined || (strict && !rendersOnItsOwn(slot.object.latex))) {
      unrepresentable.push(`${kind}${digits}`);
      return "";
    }
    allowedHrefs.add(`/objects/${slot.object.id}`);
    covered.add(`${kind}${digits}`);
    return reference(slot.object.id, slot.object.latex);
  });

  if (unrepresentable.length > 0) return null;
  const everyOperandAppears = covered.size === relation.inputs.length + relation.outputs.length;
  if (strict && !everyOperandAppears) return null;

  try {
    return katex
      .renderToString(source, {
        throwOnError: strict,
        displayMode: false,
        output: "html",
        macros: {
          "\\op": operatorIsCurrent
            ? `\\htmlClass{${CURRENT_CLASS}}{#1}`
            : `\\href{${operatorHref}}{#1}`,
        },
        strict: (code: string) => (code === "htmlExtension" ? "ignore" : "warn"),
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

function defaultTemplate(relation: RelationOut): string {
  const operands = (kind: string, count: number) =>
    Array.from({ length: count }, (_slot, i) => `{${kind}${String(i)}}`).join(",\\;");
  return [
    operands("in", relation.inputs.length),
    "\\op{\\longrightarrow}",
    operands("out", relation.outputs.length),
  ].join(" ");
}

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
