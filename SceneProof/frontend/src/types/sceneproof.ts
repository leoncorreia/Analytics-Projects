export type JobStatus =
  | 'pending'
  | 'reviewing'
  | 'review_ready'
  | 'generating'
  | 'completed'
  | 'failed'

export type AssetType = 'storyboard' | 'video' | 'avatar' | 'narration' | 'assembled'

export type ValidationSeverity = 'info' | 'warning' | 'error'

export interface CitationReference {
  citation_id: string
  source_excerpt: string
  section_hint?: string | null
  page_hint?: number | null
  char_start?: number | null
  char_end?: number | null
}

export interface SourceDocument {
  document_id: string
  filename?: string | null
  mime_type?: string | null
  normalized_text: string
  sections: string[]
  language: string
  char_count: number
}

export interface ExtractedInsights {
  goals: string[]
  required_steps: string[]
  constraints: string[]
  forbidden_claims: string[]
  key_entities: string[]
  warnings: string[]
  summary?: string | null
  demo_synthetic: boolean
}

export interface Scene {
  scene_id: string
  title: string
  objective: string
  narration: string
  visual_prompt: string
  asset_type: AssetType
  duration_estimate: number
  source_support: CitationReference[]
  risk_flags: string[]
}

export interface ScenePlan {
  plan_id: string
  scenes: Scene[]
  audience: string
  language: string
  style_preset: string
  demo_synthetic: boolean
}

export interface StoryboardFrame {
  frame_id: string
  scene_id: string
  image_asset_id: string
  prompt_used: string
  order: number
}

export interface NarrationTrack {
  track_id: string
  scene_id?: string | null
  text: string
  audio_asset_id: string
  voice_profile?: string | null
  language: string
}

export interface MediaAsset {
  asset_id: string
  scene_id?: string | null
  asset_type: AssetType
  uri: string
  mime_type?: string | null
  duration_seconds?: number | null
  width?: number | null
  height?: number | null
  provider: string
  demo_placeholder: boolean
}

export interface ValidationIssue {
  issue_id: string
  scene_id?: string | null
  severity: ValidationSeverity
  code: string
  message: string
  suggested_fix?: string | null
}

export interface AssemblyManifest {
  final_video_asset_id?: string | null
  subtitle_asset_id?: string | null
  transcript_text: string
  chapters: Record<string, unknown>[]
}

export interface GenerationResult {
  job_id: string
  scene_plan?: ScenePlan | null
  storyboard_frames: StoryboardFrame[]
  narration_tracks: NarrationTrack[]
  media_assets: MediaAsset[]
  validation_issues: ValidationIssue[]
  assembly?: AssemblyManifest | null
  demo_mode: boolean
}

export interface JobProgress {
  stage: string
  percent: number
  message: string
}

export interface Job {
  job_id: string
  status: JobStatus
  created_at: string
  updated_at: string
  audience: string
  language: string
  style_preset: string
  presenter_image_path?: string | null
  source?: SourceDocument | null
  insights?: ExtractedInsights | null
  progress: JobProgress
  error?: string | null
  result?: GenerationResult | null
  meta: Record<string, unknown>
}
