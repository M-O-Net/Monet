import createFetchClient from "openapi-fetch";
import createReactQueryClient from "openapi-react-query";

// Generic over Paths rather than owning a fixed schema — the consuming app supplies
// its own generated openapi-typescript `paths` type. Not one hand-written hook per
// endpoint: every route gets typed useQuery/useMutation for free from the schema.
export function createApiClient<Paths extends object>(baseUrl: string) {
  const fetchClient = createFetchClient<Paths>({ baseUrl });
  return createReactQueryClient(fetchClient);
}

interface ApiErrorShape {
  detail?: string;
}

function isApiErrorShape(value: unknown): value is ApiErrorShape {
  return typeof value === "object" && value !== null && "detail" in value;
}

export function formatApiError(error: unknown): string {
  if (isApiErrorShape(error) && typeof error.detail === "string") {
    return error.detail;
  }
  return "Something went wrong.";
}
