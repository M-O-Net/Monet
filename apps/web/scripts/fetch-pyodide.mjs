import { createHash } from "node:crypto";
import { copyFile, mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = join(webRoot, "..", "..");
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

// The sandbox frame runs on an opaque origin, so it can only load these assets if every serving
// environment sets Access-Control-Allow-Origin and serves .mjs as JavaScript. Each environment
// configures that separately, and a missing one fails only there, silently, at runtime. Assert it
// here instead — this runs whenever the assets themselves are assembled.
const SERVING_REQUIREMENTS = [
  { file: join(webRoot, "vite.config.ts"), needs: ["Access-Control-Allow-Origin"], env: "dev" },
  {
    file: join(webRoot, "nginx.conf"),
    needs: ["Access-Control-Allow-Origin", "\\.mjs$"],
    env: "Docker",
  },
  { file: join(repoRoot, "render.yaml"), needs: ["Access-Control-Allow-Origin"], env: "Render" },
];

for (const { file, needs, env } of SERVING_REQUIREMENTS) {
  const config = await readFile(file, "utf8").catch(() => null);
  if (config === null) throw new Error(`pyodide: ${env} serving config is missing: ${file}`);
  for (const needle of needs) {
    if (!config.includes(needle)) {
      throw new Error(
        `pyodide: ${file} no longer sets ${needle}. The translator sandbox loads its assets from ` +
          `an opaque origin, so without it the sandbox fails to start in ${env} only, with ` +
          `"Failed to fetch dynamically imported module" and nothing else to go on.`,
      );
    }
  }
}

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
