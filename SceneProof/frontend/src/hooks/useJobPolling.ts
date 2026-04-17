import { useEffect, useRef, useState } from 'react'
import { fetchJob } from '../api/client'
import type { Job, JobStatus } from '../types/sceneproof'

const ACTIVE: JobStatus[] = ['reviewing', 'generating']

export function useJobPolling(jobId: string | undefined, intervalMs = 1200) {
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timer = useRef<number | null>(null)

  useEffect(() => {
    if (!jobId) return

    let cancelled = false

    const tick = async () => {
      try {
        const j = await fetchJob(jobId)
        if (cancelled) return
        setJob(j)
        setError(null)
        if (!ACTIVE.includes(j.status)) {
          if (timer.current) window.clearInterval(timer.current)
          timer.current = null
        }
      } catch (e) {
        if (cancelled) return
        setError(e instanceof Error ? e.message : 'Failed to load job')
      }
    }

    void tick()
    timer.current = window.setInterval(() => void tick(), intervalMs)
    return () => {
      cancelled = true
      if (timer.current) window.clearInterval(timer.current)
    }
  }, [jobId, intervalMs])

  return { job, error }
}
