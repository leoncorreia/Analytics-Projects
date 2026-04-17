import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createJob } from '../api/client'
import { Button } from '../components/Button'
import { Card } from '../components/Card'

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
]

const STYLES = ['corporate', 'clinical', 'field_ops', 'executive']

export function UploadPage() {
  const navigate = useNavigate()
  const [rawText, setRawText] = useState('')
  const [audience, setAudience] = useState('New hires — operations')
  const [language, setLanguage] = useState('en')
  const [stylePreset, setStylePreset] = useState('corporate')
  const [file, setFile] = useState<File | null>(null)
  const [presenter, setPresenter] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async () => {
    setBusy(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('audience', audience)
      fd.append('language', language)
      fd.append('style_preset', stylePreset)
      if (rawText.trim()) fd.append('raw_text', rawText)
      if (file) fd.append('document', file)
      if (presenter) fd.append('presenter_image', presenter)
      const job = await createJob(fd)
      navigate(`/job/${job.job_id}/review`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not create job')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid">
      <Card title="Ingest policy or SOP" subtitle="Upload a PDF or paste raw text. Everything runs locally in demo mode without API keys.">
        <div className="form-grid">
          <label className="field">
            <span>Audience</span>
            <input value={audience} onChange={(e) => setAudience(e.target.value)} placeholder="Who is this training for?" />
          </label>
          <label className="field">
            <span>Language</span>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map((l) => (
                <option key={l.value} value={l.value}>
                  {l.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Style preset</span>
            <select value={stylePreset} onChange={(e) => setStylePreset(e.target.value)}>
              {STYLES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="field span-2">
            <span>Policy PDF (optional if text provided)</span>
            <input type="file" accept=".pdf,.txt,.md" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
          <label className="field span-2">
            <span>Presenter image (optional)</span>
            <input type="file" accept="image/*" onChange={(e) => setPresenter(e.target.files?.[0] ?? null)} />
          </label>
          <label className="field span-2">
            <span>Raw text</span>
            <textarea
              rows={10}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste SOP / policy text here..."
            />
          </label>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="actions">
          <Button disabled={busy || (!rawText.trim() && !file)} onClick={() => void onSubmit()}>
            {busy ? 'Creating…' : 'Generate plan'}
          </Button>
        </div>
      </Card>
      <aside className="aside">
        <Card title="How SceneProof works">
          <ol className="steps">
            <li>Extract rules with Seed 2.0 (demo heuristics offline).</li>
            <li>Plan scenes with citations to your source.</li>
            <li>Storyboard with Seedream, narration with Seed Speech, video with Seedance.</li>
            <li>Optional OmniHuman presenter when you supply a photo.</li>
            <li>Validate every scene, then assemble a polished training package.</li>
          </ol>
        </Card>
      </aside>
    </div>
  )
}
