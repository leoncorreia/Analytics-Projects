import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'ghost' | 'danger'

export function Button({
  children,
  variant = 'primary',
  ...rest
}: { children: ReactNode; variant?: Variant } & ButtonHTMLAttributes<HTMLButtonElement>) {
  const cls =
    variant === 'primary'
      ? 'btn btn-primary'
      : variant === 'danger'
        ? 'btn btn-danger'
        : 'btn btn-ghost'
  return (
    <button className={cls} type="button" {...rest}>
      {children}
    </button>
  )
}
