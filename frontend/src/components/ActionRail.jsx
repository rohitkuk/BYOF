import { useState } from 'react'

const ACTIONS = [
  { type: 'like', label: 'Like',  icon: 'favorite',  activeColor: 'var(--like-active)' },
  { type: 'save', label: 'Save',  icon: 'bookmark',  activeColor: 'var(--save-active)' },
  { type: 'skip', label: 'Skip',  icon: 'close',     activeColor: 'var(--text-dim)' },
]

export function ActionRail({ item, onSignal }) {
  const [liked,   setLiked]   = useState(false)
  const [saved,   setSaved]   = useState(false)
  const [skipped, setSkipped] = useState(false)

  const handle = (type) => {
    if (type === 'like')  { const n = !liked;   setLiked(n);   onSignal?.({ liked: n, saved, skipped }) }
    if (type === 'save')  { const n = !saved;   setSaved(n);   onSignal?.({ liked, saved: n, skipped }) }
    if (type === 'skip')  { const n = !skipped; setSkipped(n); onSignal?.({ liked, saved, skipped: n }) }
  }

  const state = { like: liked, save: saved, skip: skipped }

  return (
    <div style={{
      position: 'fixed', right: '16px',
      bottom: 'calc(var(--bottom-nav-height) + 80px)',
      display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'center',
      zIndex: 40,
      background: 'rgba(29,32,34,0.65)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderRadius: 'var(--radius-full)',
      border: '1px solid rgba(255,255,255,0.06)',
      padding: '8px',
    }}>
      {ACTIONS.map(({ type, label, icon, activeColor }) => {
        const active = state[type]
        return (
          <ActionBtn
            key={type}
            label={label}
            icon={icon}
            active={active}
            activeColor={activeColor}
            onClick={() => handle(type)}
          />
        )
      })}
    </div>
  )
}

function ActionBtn({ label, icon, active, activeColor, onClick }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={e => { e.stopPropagation(); onClick() }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      aria-label={label}
      style={{
        width: '48px', height: '48px',
        borderRadius: '50%',
        background: hovered ? 'rgba(255,255,255,0.12)' : 'none',
        border: 'none',
        cursor: 'pointer',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        transform: hovered ? 'scale(1.1)' : 'scale(1)',
        transition: 'transform 150ms, background 150ms',
        padding: 0, gap: '2px',
      }}
    >
      <span
        className={`material-symbols-outlined ${active ? 'icon-filled' : ''}`}
        style={{ fontSize: '24px', color: active ? activeColor : 'var(--text-primary)', transition: 'color 150ms' }}
      >
        {icon}
      </span>
      <span style={{
        fontFamily: "'Hanken Grotesk', sans-serif",
        fontSize: '9px', textTransform: 'uppercase',
        color: active ? activeColor : 'var(--text-dim)',
        letterSpacing: '0.04em',
        transition: 'color 150ms',
      }}>
        {label}
      </span>
    </button>
  )
}
