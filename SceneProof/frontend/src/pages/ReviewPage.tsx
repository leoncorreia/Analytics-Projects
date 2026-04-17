import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { runGenerate, runReview } from '../api/client'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { ProgressIndicator } from '../components/ProgressIndicator'
import { useJobPolling } from '../hooks/useJobPolling'

export function ReviewPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const { job, error } = useJobPolling(jobId)
  const [localError, setLocalError] = useState<string | null>(null)
  const [starting, setStarting] = useState(false)
  const reviewKickoff = useRef(false)

  useEffect(() => {
    if (!jobId || !job) return
    if (job.status !== 'pending' || reviewKickoff.current) return
    reviewKickoff.current = true
    void runReview(jobId).catch((e) => setLocalError(e instanceof Error ? e.message : 'Review failed'))
  }, [jobId, job])

  const onGenerate = async () => {
    if (!jobId) return
    setStarting(true)
    setLocalError(null)
    try {
      await runGenerate(jobId)
      navigate(`/job/${jobId}/output`)
    } catch (e) {
      setLocalError(e instanceof Error ? e.message : 'Could not start generation')
    } finally {
      setStarting(false)
    }
  }

  if (!jobId) return <p className="muted">Missing job id.</p>
  if (error) return <p className="error">{error}</p>
  if (!job) return <p className="muted">Loading job…</p>

  const plan = job.result?.scene_plan
  const insights = job.insights

  return (
    <div className="stack">
      <ProgressIndicator progress={job.progress} />
      {(localError || job.error) && <p className="error">{localError || job.error}</p>}
      {job.status === 'failed' && (
        <div className="actions">
          <Button
            onClick={() => {
              setLocalError(null)
              reviewKickoff.current = true
              void runReview(jobId).catch((e) =>
                setLocalError(e instanceof Error ? e.message : 'Retry failed'),
              )
            }}
          >
            Retry review
          </Button>
        </div>
      )}

      {insights && (
        <div className="grid two">
          <Card title="Key points">
            <TagList items={insights.goals} label="Goals" />
            <TagList items={insights.key_entities} label="Entities" />
            {insights.summary && <p className="muted">{insights.summary}</p>}
          </Card>
          <Card title="Required steps & guardrails">
            <TagList items={insights.required_steps} label="Steps" ordered />
            <TagList items={insights.constraints} label="Constraints" />
            <TagList items={insights.forbidden_claims} label="Forbidden claims" />
            <TagList items={insights.warnings} label="Warnings" variant="warn" />
          </Card>
        </div>
      )}

      {plan && (
        <Card title="Scene plan" subtitle="Each scene carries narration, visuals, and explicit source support.">
          <div className="timeline">
            {plan.scenes.map((scene, idx) => (
              <div key={scene.scene_id} className="scene-row">
                <div className="scene-index">{idx + 1}</div>
                <div>
                  <div className="scene-title">{scene.title}</div>
                  <p className="muted small">{scene.objective}</p>
                  <p>{scene.narration}</p>
                  <div className="pill-row">
                    <span className="pill">{scene.asset_type}</span>
                    <span className="pill">~{scene.duration_estimate}s</span>
                    {scene.risk_flags.map((r) => (
                      <span key={r} className="pill warn">
                        {r}
                      </span>
                    ))}
                  </div>
                  <div className="citations">
                    {scene.source_support.map((c) => (
                      <blockquote key={c.citation_id}>
                        <div className="muted small">{c.section_hint || 'Source'}</div>
                        {c.source_excerpt}
                      </blockquote>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="actions">
        <Button disabled={job.status !== 'review_ready' || starting} onClick={() => void onGenerate()}>
          {starting ? 'Starting…' : 'Run full generation'}
        </Button>
        <Button variant="ghost" onClick={() => navigate('/')}>
          New upload
        </Button>
      </div>
    </div>
  )
}

function TagList({
  items,
  label,
  ordered,
  variant,
}: {
  items: string[]
  label: string
  ordered?: boolean
  variant?: 'warn'
}) {
  if (!items?.length) return null
  const ListTag = ordered ? 'ol' : 'ul'
  return (
    <div className="tag-block">
      <div className={`muted small ${variant === 'warn' ? 'warn' : ''}`}>{label}</div>
      <ListTag className={ordered ? 'ol' : 'ul'}>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ListTag>
    </div>
  )
}
