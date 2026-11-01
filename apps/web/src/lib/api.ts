import { createApiClient } from "@monet/api-client";

import type { paths } from "../client/schema";

export const apiBaseUrl =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export const api = createApiClient<paths>(apiBaseUrl);
