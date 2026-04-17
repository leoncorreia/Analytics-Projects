import type { GenerationResult, Job } from '../types/sceneproof'
import { apiUrl } from '../lib/apiBase'

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json()
    if (typeof data?.detail === 'string') return data.detail
    if (Array.isArray(data?.detail)) return data.detail.map((d: { msg?: string }) => d.msg).join('; ')
    return res.statusText
  } catch {
    return res.statusText
  }
}

export async function createJob(form: FormData): Promise<Job> {
  const res = await fetch(apiUrl('/api/jobs'), { method: 'POST', body: form })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function fetchJob(jobId: string): Promise<Job> {
  const res = await fetch(apiUrl(`/api/jobs/${jobId}`))
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function runReview(jobId: string): Promise<Job> {
  const res = await fetch(apiUrl(`/api/jobs/${jobId}/review`), { method: 'POST' })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function runGenerate(jobId: string): Promise<Job> {
  const res = await fetch(apiUrl(`/api/jobs/${jobId}/generate`), { method: 'POST' })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function fetchResult(jobId: string): Promise<GenerationResult> {
  const res = await fetch(apiUrl(`/api/jobs/${jobId}/result`))
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function fetchHealth(): Promise<unknown> {
  const res = await fetch(apiUrl('/api/health'))
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}

export async function regenerateScene(jobId: string, sceneId: string): Promise<unknown> {
  const res = await fetch(apiUrl(`/api/jobs/${jobId}/regenerate-scene/${sceneId}`), {
    method: 'POST',
  })
  if (!res.ok) throw new Error(await parseError(res))
  return res.json()
}
