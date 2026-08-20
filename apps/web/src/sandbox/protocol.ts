export interface ImplementationCode {
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

export interface ProbeResult {
  applicable: string[];
}

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
