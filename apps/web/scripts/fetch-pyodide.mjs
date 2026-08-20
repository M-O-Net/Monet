import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(webRoot, "node_modules", "pyodide");
const dest = join(webRoot, "public", "pyodide");

const RUNTIME = [
  "pyodide.mjs",
  "pyodide.asm.mjs",
  "pyodide.asm.wasm",
  "python_stdlib.zip",
  "pyodide-lock.json",
];
const PACKAGES = ["sympy", "mpmath"];

const sha256 = (buf) => createHash("sha256").update(buf).digest("hex");
const exists = (p) =>
  stat(p).then(
    () => true,
    () => false,
  );
const sameFile = async (a, b) => {
  const [x, y] = await Promise.all([stat(a).catch(() => null), stat(b).catch(() => null)]);
  return x !== null && y !== null && x.size === y.size;
};

const { version } = JSON.parse(await readFile(join(src, "package.json"), "utf8"));
const lock = JSON.parse(await readFile(join(src, "pyodide-lock.json"), "utf8"));

const runtimeUpToDate = (
  await Promise.all(RUNTIME.map((f) => sameFile(join(src, f), join(dest, f))))
).every(Boolean);

if (!runtimeUpToDate) {
  await mkdir(dest, { recursive: true });
  for (const file of RUNTIME) await copyFile(join(src, file), join(dest, file));
}

for (const name of PACKAGES) {
  const pkg = lock.packages[name];
  if (!pkg) throw new Error(`${name} is not in this Pyodide release's lockfile`);
  const target = join(dest, pkg.file_name);

  if (await exists(target)) {
    if (sha256(await readFile(target)) === pkg.sha256) continue;
    console.warn(`pyodide: ${pkg.file_name} failed its checksum, refetching`);
  }

  const url = `https://cdn.jsdelivr.net/pyodide/v${version}/full/${pkg.file_name}`;
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} -> ${response.status} ${response.statusText}`);
  const bytes = Buffer.from(await response.arrayBuffer());

  const got = sha256(bytes);
  if (got !== pkg.sha256) {
    throw new Error(`${pkg.file_name} checksum mismatch: got ${got}, lockfile says ${pkg.sha256}`);
  }
  await writeFile(target, bytes);
  console.log(`pyodide: fetched ${pkg.file_name} (${pkg.version})`);
}

const files = (await readdir(dest)).length;
console.log(
  `pyodide: ${files} files in public/pyodide (runtime ${version}, sympy ${lock.packages.sympy.version})`,
);
