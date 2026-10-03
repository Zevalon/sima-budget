const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

let csrfToken: string | null = null;

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function setCsrfToken(value: string | null) {
  csrfToken = value;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  options: { csrf?: boolean } = {},
): Promise<T> {
  const headers = new Headers(init.headers);

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (options.csrf && csrfToken) {
    headers.set("X-CSRF-Token", csrfToken);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let code = "HTTP_ERROR";
    let message = "Permintaan tidak dapat diproses.";

    try {
      const problem = (await response.json()) as {
        code?: string;
        detail?: string;
      };
      code = problem.code ?? code;
      message = problem.detail ?? message;
    } catch {
      // Keep the generic error message for non-JSON failures.
    }

    throw new ApiError(response.status, code, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
