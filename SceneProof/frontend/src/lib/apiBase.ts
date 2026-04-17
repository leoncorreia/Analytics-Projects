/**
 * Production: set `VITE_API_BASE_URL` to your Render (or other) API origin, e.g.
 * `https://sceneproof-api.onrender.com` — no trailing slash.
 * Dev: leave unset so `/api` and `/media` use Vite’s proxy to localhost.
 */
const raw = import.meta.env.VITE_API_BASE_URL as string | undefined

export const API_ORIGIN = (raw ?? '').trim().replace(/\/$/, '')

export function apiUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`
  return API_ORIGIN ? `${API_ORIGIN}${p}` : p
}

/** Map stored job asset paths to a browser URL (same host as API in production). */
export function publicMediaUrl(uri: string): string {
  if (uri.startsWith('http://') || uri.startsWith('https://')) return uri
  const clean = uri.replace(/^\/+/, '')
  const prefix = API_ORIGIN ? `${API_ORIGIN}/media` : '/media'
  return `${prefix}/${clean}`
}
