import { appConfig } from '../config/env';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

type RequestOptions = Omit<RequestInit, 'body'> & { body?: unknown };

/** Central API boundary. Uses same-site cookies; it never reads tokens from local storage. */
export async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers, ...requestOptions } = options;
  const response = await fetch(`${appConfig.apiBaseUrl}${path}`, {
    ...requestOptions,
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => undefined) as { detail?: string; code?: string } | undefined;
    throw new ApiError(payload?.detail || `Request failed (${response.status})`, response.status, payload?.code);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
