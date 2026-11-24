export async function api<T>(path: string, options: { token?: string; body?: object } = {}): Promise<T> {
  const headers = new Headers({ Accept: 'application/json' })
  if (options.token) headers.set('Authorization', `Bearer ${options.token}`)
  if (options.body) headers.set('Content-Type', 'application/json')
  const response = await fetch(`/api/v1${path}`, {
    method: options.body ? 'POST' : 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(typeof payload?.detail === 'string' ? payload.detail : `Request failed (HTTP ${response.status}).`)
  }
  return response.status === 204 ? undefined as T : await response.json()
}

export async function listAll<T>(path: string): Promise<T[]> {
  const results: T[] = []
  for (let offset = 0; ; offset += 100) {
    const page = await api<T[]>(`${path}?limit=100&offset=${offset}`)
    results.push(...page)
    if (page.length < 100) return results
  }
}
