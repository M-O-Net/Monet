import { useSyncExternalStore } from "react";

import { getStatus, subscribe, type SandboxStatus } from "./client";

/** Re-renders when the sandbox starts, becomes ready, or fails. */
export function useSandboxStatus(): SandboxStatus {
  return useSyncExternalStore(subscribe, getStatus, () => "idle" as const);
}
