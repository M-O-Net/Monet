// The document loaded into <iframe sandbox="allow-scripts"> — deliberately without
// allow-same-origin, which gives this document an opaque origin. That is the boundary that makes
// running stranger-authored Python safe: no access to the app's localStorage or DOM, and every
// request to the Monet API counts as cross-origin, so the API's CORS allowlist rejects it at
// preflight.
//
// Pyodide runs here on the frame's own thread rather than in a Worker, because an opaque origin
// cannot load a worker script at all: Chrome refuses to construct a module worker from one, and
// importScripts on a blob:null worker is blocked regardless of CORS headers. The time limit that
// a Worker's terminate() would have provided is enforced inside Python instead — see the deadline
// guard in runner.py.

import preludeSource from "./prelude.py?raw";
import runnerSource from "./runner.py?raw";
import { type SandboxRequest, type SandboxResponse } from "./protocol";

interface PyodideApi {
  loadPackage: (names: string[]) => Promise<unknown>;
  runPython: (code: string) => unknown;
  globals: { get: (name: string) => ((...args: string[]) => string) | undefined };
}

// location.origin is "null" here, so an absolute path would not resolve; location.href still
// carries the real URL.
const indexURL = new URL("/pyodide/", location.href).href;

const reply = (message: SandboxResponse) => {
  parent.postMessage(message, "*");
};

function describe(error: unknown): string {
  if (error instanceof Error) {
    // Pyodide puts the whole Python traceback in the message; the last line is what someone
    // debugging their own implementation actually wants to read.
    const lines = error.message.trimEnd().split("\n");
    return lines[lines.length - 1] || error.message;
  }
  return String(error);
}

const ready = (async () => {
  const module = (await import(/* @vite-ignore */ `${indexURL}pyodide.mjs`)) as {
    loadPyodide: (options: { indexURL: string }) => Promise<PyodideApi>;
  };
  const pyodide = await module.loadPyodide({ indexURL });
  await pyodide.loadPackage(["sympy"]);
  pyodide.runPython(preludeSource);
  pyodide.runPython(runnerSource);
  return pyodide;
})();

ready.then(
  () => {
    reply({ kind: "ready" });
  },
  (error: unknown) => {
    reply({ kind: "result", id: "boot", ok: false, error: describe(error) });
  },
);

function call(pyodide: PyodideApi, name: string, ...args: string[]): unknown {
  const fn = pyodide.globals.get(name);
  if (!fn) throw new Error(`sandbox runner is missing ${name}()`);
  return JSON.parse(fn(...args)) as unknown;
}

function handle(request: SandboxRequest, pyodide: PyodideApi): unknown {
  if (request.kind === "probe") {
    return call(pyodide, "probe", request.latex, JSON.stringify(request.implementations));
  }
  return call(pyodide, "run", request.code, JSON.stringify(request.inputs));
}

window.addEventListener("message", (event: MessageEvent<SandboxRequest>) => {
  // No origin check: only the embedding page can reach this frame, and an opaque-origin document
  // cannot verify an origin anyway. Nothing here is privileged — the worst a forged message can
  // do is compute an answer inside the sandbox.
  const request = event.data;
  void (async () => {
    try {
      const value = handle(request, await ready);
      reply({ kind: "result", id: request.id, ok: true, value: value as never });
    } catch (error: unknown) {
      reply({ kind: "result", id: request.id, ok: false, error: describe(error) });
    }
  })();
});
