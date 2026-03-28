/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Public API origin for production (e.g. https://your-api.onrender.com). Omit in dev to use Vite proxy. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
