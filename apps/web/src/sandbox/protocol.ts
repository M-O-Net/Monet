export interface SandboxValue {
  latex: string;
  data: Record<string, unknown> | null;
}

export interface ImplementationCode {
  id: string;
  code: string;
}

export interface ProbeRequest {
  id: string;
  kind: "probe";
  input: SandboxValue;
  implementations: ImplementationCode[];
}

export interface RunRequest {
  id: string;
  kind: "run";
  code: string;
  inputs: SandboxValue[];
}

export interface DescribeRequest {
  id: string;
  kind: "describe";
  latex: string;
}

export type SandboxRequest = ProbeRequest | RunRequest | DescribeRequest;

export interface ProbeResult {
  applicable: string[];
}

export interface RunResult {
  outputs: SandboxValue[];
}

export type SandboxResponse =
  | { kind: "ready" }
  | { kind: "result"; id: string; ok: true; value: ProbeResult | RunResult | SandboxValue }
  | { kind: "result"; id: string; ok: false; error: string };

export function isSandboxResponse(value: unknown): value is SandboxResponse {
  if (typeof value !== "object" || value === null || !("kind" in value)) return false;
  const { kind } = value;
  return kind === "ready" || kind === "result";
}
