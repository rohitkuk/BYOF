import { memo } from 'react'

export const ProgressDots = memo(function ProgressDots({ total, current }) {
  const capped = Math.min(total, 30)
  return (
    <div
      className="desktop-only"
      style={{
        position: 'fixed',
        right: '32px',
        top: '50%', transform: 'translateY(-50%)',
        display: 'flex', flexDirection: 'column', gap: '12px',
        zIndex: 40,
      }}
    >
      {Array.from({ length: capped }, (_, i) => (
        <div
          key={i}
          style={{
            width: '8px',
            height: i === current ? '48px' : '8px',
            background: i === current ? 'var(--secondary)' : 'var(--surface-highest)',
            borderRadius: '9999px',
            transition: 'height 200ms cubic-bezier(0.4,0,0.2,1), background 200ms',
            cursor: 'default',
          }}
        />
      ))}
    </div>
  )
})
