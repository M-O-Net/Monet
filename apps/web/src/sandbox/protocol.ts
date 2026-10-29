export interface SandboxValue {
  latex: string;
  data: Record<string, unknown> | null;
}

export interface SandboxObject {
  latex: string;
  facets: Record<string, unknown>[];
}

export interface ImplementationCode {
  id: string;
  code: string;
}

export interface ProbeRequest {
  id: string;
  kind: "probe";
  input: SandboxObject;
  implementations: ImplementationCode[];
}

export interface RunRequest {
  id: string;
  kind: "run";
  code: string;
  inputs: SandboxObject[];
}

export interface DescribeRequest {
  id: string;
  kind: "describe";
  latex: string;
}

export interface AnalyzeRequest {
  id: string;
  kind: "analyze";
  input: SandboxValue;
}

export type SandboxRequest = ProbeRequest | RunRequest | DescribeRequest | AnalyzeRequest;

export interface ProbeResult {
  applicable: string[];
}

export interface RunResult {
  outputs: SandboxValue[];
}

export interface RealRoot {
  x: number;
  latex: string | null;
  multiplicity: number;
}

export interface ComplexRoot {
  re: number;
  im: number;
  latex: string | null;
  multiplicity: number;
}

export interface Analysis {
  variable: string;
  window: [number, number];
  points: [number, number | null][];
  real_roots: RealRoot[];
  complex_roots: ComplexRoot[] | null;
}

export type SandboxResponse =
  | { kind: "ready" }
  | {
      kind: "result";
      id: string;
      ok: true;
      value: ProbeResult | RunResult | SandboxValue | Analysis | null;
    }
  | { kind: "result"; id: string; ok: false; error: string };

export function isSandboxResponse(value: unknown): value is SandboxResponse {
  if (typeof value !== "object" || value === null || !("kind" in value)) return false;
  const { kind } = value;
  return kind === "ready" || kind === "result";
}
