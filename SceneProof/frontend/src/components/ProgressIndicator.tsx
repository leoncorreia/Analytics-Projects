import type { JobProgress } from '../types/sceneproof'

export function ProgressIndicator({ progress }: { progress: JobProgress }) {
  const pct = Math.max(0, Math.min(100, progress.percent))
  return (
    <div className="progress-wrap">
      <div className="progress-meta">
        <span className="pill">{progress.stage}</span>
        <span className="muted">{progress.message}</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
