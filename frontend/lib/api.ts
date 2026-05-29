/**
 * Fetch wrapper for FastAPI backend calls.
 *
 * In development, Next.js rewrites `/api/*` to `http://localhost:8000/api/*`
 * (configured in next.config.js), so all calls are same-origin.
 */

const API_BASE = "";

export async function apiFetch<T = unknown>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    const message =
      errorBody?.detail ?? errorBody?.error ?? `API error: ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export function apiGet<T = unknown>(
  path: string,
  params?: Record<string, string | number | undefined>,
): Promise<T> {
  const searchParams = new URLSearchParams();
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== "") {
        searchParams.set(key, String(value));
      }
    }
  }
  const query = searchParams.toString();
  return apiFetch<T>(query ? `${path}?${query}` : path);
}

export function apiPost<T = unknown>(
  path: string,
  body: unknown,
): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
