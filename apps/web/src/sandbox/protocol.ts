// Messages crossing the sandbox boundary. The frame runs on an opaque origin, so postMessage
// is the only channel between it and the app — everything here has to survive structured clone.

export interface ImplementationCode {
  /** The operator's object id — an implementation has no id of its own. */
  id: string;
  code: string;
}

export interface ProbeRequest {
  id: string;
  kind: "probe";
  latex: string;
  implementations: ImplementationCode[];
}

export interface RunRequest {
  id: string;
  kind: "run";
  code: string;
  inputs: string[];
}

export type SandboxRequest = ProbeRequest | RunRequest;

/** Ids of the implementations whose `accepts` returned true for the probed object. */
export interface ProbeResult {
  applicable: string[];
}

/** LaTeX strings returned by `compute`, in output order. */
export interface RunResult {
  outputs: string[];
}

export type SandboxResponse =
  | { kind: "ready" }
  | { kind: "result"; id: string; ok: true; value: ProbeResult | RunResult }
  | { kind: "result"; id: string; ok: false; error: string };

export function isSandboxResponse(value: unknown): value is SandboxResponse {
  if (typeof value !== "object" || value === null || !("kind" in value)) return false;
  const { kind } = value;
  return kind === "ready" || kind === "result";
}
