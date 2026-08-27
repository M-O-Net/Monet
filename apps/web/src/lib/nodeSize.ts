const MATRIX_ENV = /\\begin\{[pbv]?matrix\}(.*?)\\end\{[pbv]?matrix\}/s;
const MACRO = /\\[a-zA-Z]+/g;
const GROUPING = /[{}$^_\\]/g;

const CHARACTER_WIDTH = 9;
const CELL_WIDTH = 26;
const ROW_HEIGHT = 20;
const MATRIX_CHROME = 26;
const TEXT_HEIGHT = 22;
const MIN_WIDTH = 34;
const MAX_WIDTH = 190;

export interface NodeSize {
  width: number;
  height: number;
}

export function estimateNodeSize(latex: string, scale = 1): NodeSize {
  const matrix = MATRIX_ENV.exec(latex);
  if (matrix !== null) {
    const rows = matrix[1].split("\\\\");
    const columns = Math.max(...rows.map((row) => row.split("&").length));
    return {
      width: Math.min(MAX_WIDTH, MATRIX_CHROME + columns * CELL_WIDTH) * scale,
      height: Math.max(TEXT_HEIGHT, rows.length * ROW_HEIGHT) * scale,
    };
  }

  const visible = latex.replace(MACRO, " ").replace(GROUPING, "").trim();
  return {
    width: Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, 14 + visible.length * CHARACTER_WIDTH)) * scale,
    height: TEXT_HEIGHT * scale,
  };
}

export const sizeRadius = (size: NodeSize): number => Math.hypot(size.width, size.height) / 2;
