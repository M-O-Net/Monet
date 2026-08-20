import { useSyncExternalStore } from "react";

import { getStatus, subscribe, type SandboxStatus } from "./client";

export function useSandboxStatus(): SandboxStatus {
  return useSyncExternalStore(subscribe, getStatus, () => "idle" as const);
}
