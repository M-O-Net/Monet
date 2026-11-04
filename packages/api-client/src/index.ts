import createFetchClient from "openapi-fetch";
import createReactQueryClient from "openapi-react-query";

// Generic over Paths rather than owning a fixed schema — the consuming app supplies
// its own generated openapi-typescript `paths` type. Not one hand-written hook per
// endpoint: every route gets typed useQuery/useMutation for free from the schema.
export function createApiClient<Paths extends object>(
  baseUrl: string,
  headers: () => Record<string, string> = () => ({}),
) {
  const fetchClient = createFetchClient<Paths>({ baseUrl });
  fetchClient.use({
    onRequest({ request }) {
      for (const [name, value] of Object.entries(headers())) request.headers.set(name, value);
      return request;
    },
    async onResponse({ response }) {
      if (!response.ok) throw new ApiError(response.status, await detailOf(response));
      return undefined;
    },
  });
  return createReactQueryClient(fetchClient);
}

interface ApiErrorShape {
  detail?: string;
}

function isApiErrorShape(value: unknown): value is ApiErrorShape {
  return typeof value === "object" && value !== null && "detail" in value;
}

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string | null;

  constructor(status: number, detail: string | null) {
    super(detail ?? `the server answered with error ${String(status)}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function detailOf(response: Response): Promise<string | null> {
  try {
    const body: unknown = await response.clone().json();
    return isApiErrorShape(body) && typeof body.detail === "string" ? body.detail : null;
  } catch {
    return null;
  }
}

export function formatApiError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.detail !== null) return error.detail;
    if (error.status >= 500) {
      return `The Monet server had a problem (error ${String(error.status)}). Try again in a minute.`;
    }
    return `The Monet server refused this (error ${String(error.status)}).`;
  }
  if (error instanceof TypeError) {
    return `Could not reach the Monet server (${error.message}). Check your connection, or try again in a minute.`;
  }
  if (isApiErrorShape(error) && typeof error.detail === "string") return error.detail;
  if (error instanceof Error) return `Something went wrong: ${error.message}`;
  return "Something went wrong.";
}
