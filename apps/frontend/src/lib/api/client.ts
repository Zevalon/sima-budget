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

async function errorFromResponse(response: Response): Promise<ApiError> {
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

  return new ApiError(response.status, code, message);
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
    throw await errorFromResponse(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export type ApiDownload = {
  blob: Blob;
  filename: string;
};

function downloadFilename(response: Response): string {
  const disposition = response.headers.get("Content-Disposition");
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1] ?? "download";
}

export async function apiDownload(path: string): Promise<ApiDownload> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw await errorFromResponse(response);
  }

  return {
    blob: await response.blob(),
    filename: downloadFilename(response),
  };
}
