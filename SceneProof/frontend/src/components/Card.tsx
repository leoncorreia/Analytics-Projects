import type { ReactNode } from 'react'

export function Card({
  title,
  subtitle,
  children,
}: {
  title?: string
  subtitle?: string
  children: ReactNode
}) {
  return (
    <section className="card">
      {(title || subtitle) && (
        <header className="card-header">
          {title && <h2>{title}</h2>}
          {subtitle && <p className="muted">{subtitle}</p>}
        </header>
      )}
      <div className="card-body">{children}</div>
    </section>
  )
}
