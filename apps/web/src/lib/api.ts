import { createApiClient } from "@monet/api-client";

import type { paths } from "../client/schema";

const baseUrl = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export const api = createApiClient<paths>(baseUrl);
