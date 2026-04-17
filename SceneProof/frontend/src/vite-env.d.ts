/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Production API origin, e.g. https://sceneproof-api.onrender.com (no trailing slash). */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
