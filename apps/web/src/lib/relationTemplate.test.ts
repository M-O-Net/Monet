import { describe, expect, it } from "vitest";

import { buildTemplateHtml } from "./relationTemplate";
import type { ObjectOut, RelationOut } from "./types";

const A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";
const C = "cccccccc-cccc-4ccc-8ccc-cccccccccccc";

const object = (id: string, latex: string): ObjectOut => ({ id, latex, description: null });

function relation(inputs: ObjectOut[], outputs: ObjectOut[]): RelationOut {
  return {
    id: "11111111-1111-4111-8111-111111111111",
    operator: object("22222222-2222-4222-8222-222222222222", "\\text{Matrix Addition}"),
    inputs: inputs.map((obj, position) => ({ position, object: obj })),
    outputs: outputs.map((obj, position) => ({ position, object: obj })),
    display: null,
  };
}

const addition = relation([object(A, "A"), object(B, "B")], [object(C, "C")]);

describe("buildTemplateHtml", () => {
  it("renders the operands into the template as links", () => {
    const html = buildTemplateHtml("{in0} + {in1} = {out0}", addition);
    expect(html).not.toBeNull();
    expect(html).toContain(`href="/objects/${A}"`);
    expect(html).toContain(`href="/objects/${B}"`);
    expect(html).toContain(`href="/objects/${C}"`);
  });

  it("keeps binary-operator spacing, which typesetting the pieces separately would lose", () => {
    const html = buildTemplateHtml("{in0} + {in1} = {out0}", addition);
    // A lone " + " renders as an ordinary symbol with no spacing at all; it is only a binary
    // operator when KaTeX sees the whole expression at once.
    expect(html).toContain("mbin");
    expect(html).toContain("mspace");
  });

  it("substitutes inside a group, which splitting on placeholders cannot express", () => {
    // Splitting would hand KaTeX the fragment "\frac{" and throw a ParseError.
    const html = buildTemplateHtml("\\frac{{in0}}{{in1}} = {out0}", addition);
    expect(html).not.toBeNull();
    expect(html).toContain("frac");
  });

  it("allows an operand to be repeated", () => {
    const square = relation([object(A, "A")], [object(C, "C")]);
    expect(buildTemplateHtml("{in0} \\cdot {in0} = {out0}", square)).not.toBeNull();
  });

  it("links the operator's own notation when the template marks it with \\op", () => {
    const html = buildTemplateHtml("{in0} \\op{+} {in1} = {out0}", addition);
    expect(html).not.toBeNull();
    expect(html).toContain(`href="/objects/${addition.operator.id}"`);
  });

  it("renders \\op inside a superscript, where the notation is not a top-level run", () => {
    const inverse = relation([object(A, "A")], [object(C, "C")]);
    const html = buildTemplateHtml("{in0}^{\\op{-1}} = {out0}", inverse);
    expect(html).not.toBeNull();
    expect(html).toContain(`href="/objects/${inverse.operator.id}"`);
  });

  it("falls back when a placeholder is out of range", () => {
    expect(buildTemplateHtml("{in0} + {in7} = {out0}", addition)).toBeNull();
  });

  it("falls back when the template does not mention every operand", () => {
    // The template belongs to the operator but arity belongs to the relation, so a two-input
    // template applied to a three-input relation would render an equation that is false.
    expect(buildTemplateHtml("{in0} = {out0}", addition)).toBeNull();
  });

  it("falls back when an operand's own latex will not parse", () => {
    // One unparseable operand otherwise turns the entire row into red error text.
    const broken = relation([object(A, "\\frac{1}"), object(B, "B")], [object(C, "C")]);
    expect(buildTemplateHtml("{in0} + {in1} = {out0}", broken)).toBeNull();
  });

  it("refuses to emit a javascript: link smuggled in through an operand's latex", () => {
    // Object latex is user input and ends up in dangerouslySetInnerHTML. KaTeX's trust option
    // is the only thing standing between that and script execution, so it is a predicate
    // admitting nothing but the object links we built ourselves — never `true`.
    const hostile = relation(
      [object(A, "\\href{javascript:alert(1)}{click}"), object(B, "B")],
      [object(C, "C")],
    );
    const html = buildTemplateHtml("{in0} + {in1} = {out0}", hostile);
    expect(html ?? "").not.toContain("javascript:");
    for (const href of [...(html ?? "").matchAll(/href="([^"]*)"/g)].map((m) => m[1])) {
      expect(href).toMatch(/^\/objects\//);
    }
  });
});
