import { tags as t } from "@lezer/highlight";
import { createTheme } from "@uiw/codemirror-themes";

/**
 * CodeMirror dressed in Monet's own palette (see index.css's `@theme`).
 *
 * The stock light theme is a white page with browser-blue keywords, which reads as a foreign
 * widget dropped into the journal. These are the same tokens the rest of the app uses: pond for
 * syntax that structures the code, willow for strings, gold for literals, ink-soft for the
 * incidental punctuation that shouldn't compete with either.
 */
export const monetEditorTheme = createTheme({
  theme: "light",
  settings: {
    background: "transparent",
    foreground: "#23322b", // ink
    caret: "#3e6e78", // pond
    selection: "#f1e2c2", // gold-soft
    selectionMatch: "#f1e2c2",
    lineHighlight: "transparent",
    gutterBackground: "transparent",
    gutterForeground: "#a8b3a8",
    gutterBorder: "transparent",
    fontFamily: 'ui-monospace, "SF Mono", Menlo, Consolas, monospace',
  },
  styles: [
    { tag: [t.keyword, t.controlKeyword, t.moduleKeyword], color: "#2f545c" }, // pond-deep
    { tag: [t.definitionKeyword], color: "#2f545c", fontWeight: "600" },
    { tag: [t.function(t.definition(t.variableName))], color: "#23322b", fontWeight: "600" },
    { tag: [t.string, t.special(t.string)], color: "#6b8c57" }, // willow — includes docstrings
    { tag: [t.number, t.bool, t.null], color: "#be8f3e" }, // gold
    { tag: [t.comment], color: "#7d8b81", fontStyle: "italic" },
    { tag: [t.propertyName], color: "#3e6e78" }, // pond
    { tag: [t.operator, t.punctuation, t.separator, t.bracket], color: "#4c5c53" }, // ink-soft
    { tag: [t.className, t.typeName], color: "#a8452f" }, // rust
    { tag: [t.self, t.atom], color: "#2f545c" },
    { tag: [t.invalid], color: "#a8452f" },
  ],
});
