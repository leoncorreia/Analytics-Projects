import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchResult, regenerateScene } from '../api/client'
import { publicMediaUrl } from '../lib/apiBase'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { ProgressIndicator } from '../components/ProgressIndicator'
import { useJobPolling } from '../hooks/useJobPolling'
import type { GenerationResult, MediaAsset } from '../types/sceneproof'

export function OutputPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const { job, error } = useJobPolling(jobId)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [resultError, setResultError] = useState<string | null>(null)
  const fetched = useRef(false)

  useEffect(() => {
    fetched.current = false
  }, [jobId])

  useEffect(() => {
    if (!jobId || job?.status !== 'completed' || fetched.current) return
    fetched.current = true
    void fetchResult(jobId)
      .then(setResult)
      .catch((e) => setResultError(e instanceof Error ? e.message : 'Unable to load result'))
  }, [jobId, job?.status])

  const effectiveResult = result || (job?.status === 'completed' ? job.result : null)

  const storyboards = useMemo(
    () => effectiveResult?.media_assets.filter((a) => a.asset_type === 'storyboard') ?? [],
    [effectiveResult],
  )

  if (!jobId) return <p className="muted">Missing job id.</p>
  if (error) return <p className="error">{error}</p>
  if (!job) return <p className="muted">Loading job…</p>

  if (job.status === 'failed') {
    return (
      <div className="stack">
        <Card title="Generation failed">
          <p className="error">{job.error}</p>
          <Button onClick={() => navigate('/')}>Start over</Button>
        </Card>
      </div>
    )
  }

  if (job.status !== 'completed') {
    return (
      <div className="stack">
        <Card title="Rendering training package">
          <ProgressIndicator progress={job.progress} />
          <p className="muted">Polling job status…</p>
        </Card>
      </div>
    )
  }

  if (resultError) return <p className="error">{resultError}</p>
  if (!effectiveResult) return <p className="muted">Finalizing payload…</p>

  return (
    <div className="stack">
      <div className="hero-banner">
        <div>
          <p className="eyebrow">Training output</p>
          <h1>Your SceneProof package</h1>
          <p className="muted">
            {effectiveResult.demo_mode
              ? 'Demo mode: media URIs are placeholders until provider keys are configured.'
              : 'Live provider outputs attached where available.'}
          </p>
        </div>
        <div className="hero-actions">
          <Button variant="ghost" onClick={() => navigate(`/job/${jobId}/review`)}>
            Back to review
          </Button>
          <Button variant="ghost" onClick={() => navigate('/')}>
            New job
          </Button>
        </div>
      </div>

      <div className="grid two">
        <Card title="Program video" subtitle="Final stitch is metadata-first for the MVP; binary muxing plugs in behind the same interface.">
          <VideoPlaceholder assets={effectiveResult.media_assets} />
        </Card>
        <Card title="Transcript">
          <pre className="transcript">{effectiveResult.assembly?.transcript_text}</pre>
        </Card>
      </div>

      <Card title="Storyboard gallery">
        <div className="gallery">
          {storyboards.map((asset) => (
            <figure key={asset.asset_id} className="frame-card">
              <StoryboardVisual asset={asset} />
              <figcaption className="muted small">{asset.uri}</figcaption>
            </figure>
          ))}
        </div>
      </Card>

      <div className="grid two">
        <Card title="Scene list">
          <ul className="plain-list">
            {(effectiveResult.scene_plan?.scenes ?? []).map((s) => (
              <li key={s.scene_id}>
                <strong>{s.title}</strong>
                <div className="muted small">{s.objective}</div>
                <div className="row-actions">
                  <Button
                    variant="ghost"
                    onClick={() =>
                      void regenerateScene(jobId, s.scene_id).then(() =>
                        alert('Regeneration queued (placeholder).'),
                      )
                    }
                  >
                    Regenerate scene
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </Card>
        <Card title="Citations & validation">
          <h3>Validation</h3>
          <ul className="plain-list">
            {effectiveResult.validation_issues.map((issue) => (
              <li key={issue.issue_id} className={issue.severity}>
                <strong>{issue.code}</strong> — {issue.message}
                {issue.suggested_fix && <div className="muted small">Fix: {issue.suggested_fix}</div>}
              </li>
            ))}
          </ul>
          <h3>Primary citations</h3>
          <ul className="plain-list">
            {(effectiveResult.scene_plan?.scenes ?? []).flatMap((s) =>
              s.source_support.map((c) => (
                <li key={c.citation_id}>
                  <div className="muted small">{s.title}</div>
                  {c.source_excerpt}
                </li>
              )),
            )}
          </ul>
        </Card>
      </div>

      <Card title="Downloads (placeholder)">
        <p className="muted">Packaged ZIP / MP4 export will land here once the assembly worker writes binaries.</p>
        <div className="actions">
          <Button disabled>Download final MP4</Button>
          <Button disabled>Download asset bundle</Button>
        </div>
      </Card>
    </div>
  )
}

function StoryboardVisual({ asset }: { asset: MediaAsset }) {
  if (asset.demo_placeholder) {
    return <div className="placeholder-visual">{asset.scene_id}</div>
  }
  return <img src={publicMediaUrl(asset.uri)} alt={asset.scene_id || ''} loading="lazy" />
}

function VideoPlaceholder({ assets }: { assets: MediaAsset[] }) {
  const assembled = assets.find((a) => a.asset_type === 'assembled')
  const sceneVideos = assets.filter((a) => a.asset_type === 'video')
  return (
    <div className="video-shell">
      <div className="video-placeholder">
        <p>Preview track</p>
        <p className="muted small">
          {assembled?.uri ? (
            <a href={publicMediaUrl(assembled.uri)} target="_blank" rel="noreferrer">
              Open assembly manifest
            </a>
          ) : (
            'Assembly manifest pending'
          )}
        </p>
      </div>
      {sceneVideos.length > 0 && (
        <ul className="plain-list">
          {sceneVideos.map((v) => (
            <li key={v.asset_id} className="muted small">
              Scene video: <code>{v.uri}</code>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
