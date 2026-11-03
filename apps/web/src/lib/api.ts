import { createApiClient } from "@monet/api-client";

import type { paths } from "../client/schema";
import { readEditorKey } from "./editorKey";

export const apiBaseUrl =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export const api = createApiClient<paths>(apiBaseUrl, (): Record<string, string> => {
  const key = readEditorKey();
  return key === "" ? {} : { "X-Editor-Key": key };
});
