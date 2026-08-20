// App-side handle on the implementation sandbox. One hidden frame per tab, created the first time
// something actually needs it — nothing is downloaded while you're just browsing the network.
//
// The frame is created outside React on purpose: it's a browser resource with tab lifetime, like
// a service worker, not a piece of the view. See frame.ts for what makes it a boundary.

import {
  isSandboxResponse,
  type ProbeRequest,
  type ProbeResult,
  type RunRequest,
  type RunResult,
  type SandboxRequest,
  type ImplementationCode,
} from "./protocol";

// Omit<> over a union collapses to the shared keys, so the two shapes are spelled out.
type SandboxRequestBody = Omit<ProbeRequest, "id"> | Omit<RunRequest, "id">;

export type SandboxStatus = "idle" | "starting" | "ready" | "failed";

/** Pyodide boots and loads sympy on first use; everything after that is fast. */
const BOOT_TIMEOUT_MS = 90_000;
/** An implementation is a handful of sympy calls. Past this it's looping, and the frame gets killed. */
const RUN_TIMEOUT_MS = 10_000;

interface Pending {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
}

let frame: HTMLIFrameElement | undefined;
let booted: Promise<void> | undefined;
let signalBooted: (() => void) | undefined;
let failBoot: ((error: Error) => void) | undefined;
let queue: SandboxRequest[] = [];
let isReady = false;
let nextId = 0;

const pending = new Map<string, Pending>();
const listeners = new Set<(status: SandboxStatus) => void>();
let status: SandboxStatus = "idle";

function setStatus(next: SandboxStatus) {
  status = next;
  for (const listener of listeners) listener(next);
}

export function getStatus(): SandboxStatus {
  return status;
}

export function subscribe(listener: (status: SandboxStatus) => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function send(request: SandboxRequest) {
  if (isReady && frame?.contentWindow) frame.contentWindow.postMessage(request, "*");
  else queue.push(request);
}

function onMessage(event: MessageEvent<unknown>) {
  if (event.source !== frame?.contentWindow) return;
  if (!isSandboxResponse(event.data)) return;
  const message = event.data;

  if (message.kind === "ready") {
    isReady = true;
    setStatus("ready");
    signalBooted?.();
    const queued = queue;
    queue = [];
    for (const request of queued) send(request);
    return;
  }

  if (message.id === "boot") {
    failBoot?.(new Error(message.ok ? "unexpected boot reply" : message.error));
    setStatus("failed");
    return;
  }

  const entry = pending.get(message.id);
  if (!entry) return;
  pending.delete(message.id);
  clearTimeout(entry.timer);
  if (message.ok) entry.resolve(message.value);
  else entry.reject(new Error(message.error));
}

function start(): Promise<void> {
  if (booted) return booted;

  booted = new Promise<void>((resolve, reject) => {
    signalBooted = resolve;
    failBoot = reject;
    setTimeout(() => {
      reject(new Error("the sandbox took too long to start"));
    }, BOOT_TIMEOUT_MS);
  });

  window.addEventListener("message", onMessage);

  const element = document.createElement("iframe");
  // allow-scripts WITHOUT allow-same-origin is the whole boundary: it gives the frame an opaque
  // origin, so implementation code can't reach this page's storage or DOM, and its requests to the
  // Monet API are cross-origin and fail the API's CORS allowlist. Do not add allow-same-origin.
  element.setAttribute("sandbox", "allow-scripts");
  element.src = "/sandbox.html";
  element.title = "Implementation sandbox";
  element.setAttribute("aria-hidden", "true");
  element.style.display = "none";
  document.body.appendChild(element);
  frame = element;

  setStatus("starting");
  return booted;
}

/** Tear the frame down and forget it — the only way to stop an implementation that won't finish. */
function reset(reason: string) {
  for (const [, entry] of pending) {
    clearTimeout(entry.timer);
    entry.reject(new Error(reason));
  }
  pending.clear();
  queue = [];
  isReady = false;
  window.removeEventListener("message", onMessage);
  frame?.remove();
  frame = undefined;
  booted = undefined;
  signalBooted = undefined;
  failBoot = undefined;
  setStatus("idle");
}

async function request<T>(body: SandboxRequestBody): Promise<T> {
  try {
    await start();
  } catch (error) {
    setStatus("failed");
    throw error;
  }

  const id = String(nextId++);
  const result = new Promise<unknown>((resolve, reject) => {
    const timer = setTimeout(() => {
      // Killing the frame is what actually stops a runaway loop; the next call boots a new one.
      reset("the implementation ran too long and was stopped");
    }, RUN_TIMEOUT_MS);
    pending.set(id, { resolve, reject, timer });
  });

  send({ ...body, id });
  return (await result) as T;
}

/** Which of these implementations accept the given object? */
export async function probe(
  latex: string,
  implementations: ImplementationCode[],
): Promise<string[]> {
  if (implementations.length === 0) return [];
  const result = await request<ProbeResult>({ kind: "probe", latex, implementations });
  return result.applicable;
}

/** Run one implementation over its inputs; returns the output LaTeX. */
export async function run(code: string, inputs: string[]): Promise<string[]> {
  const result = await request<RunResult>({ kind: "run", code, inputs });
  return result.outputs;
}
