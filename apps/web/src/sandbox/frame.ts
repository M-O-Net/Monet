import preludeSource from "./prelude.py?raw";
import runnerSource from "./runner.py?raw";
import { type SandboxRequest, type SandboxResponse } from "./protocol";

interface PyodideApi {
  loadPackage: (names: string[]) => Promise<unknown>;
  runPython: (code: string) => unknown;
  globals: { get: (name: string) => ((...args: string[]) => string) | undefined };
}

const indexURL = new URL("/pyodide/", location.href).href;

const reply = (message: SandboxResponse) => {
  parent.postMessage(message, "*");
};

function describe(error: unknown): string {
  if (error instanceof Error) {
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
