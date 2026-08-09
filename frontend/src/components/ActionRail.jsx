import { useState } from 'react'

export function ActionRail({ item, onSignal }) {
  const [liked, setLiked] = useState(false)
  const [skipped, setSkipped] = useState(false)
  const [saved, setSaved] = useState(false)

  const toggle = (type) => {
    if (type === 'like') {
      const next = !liked
      setLiked(next)
      onSignal?.({ liked: next, skipped, saved })
    } else if (type === 'skip') {
      const next = !skipped
      setSkipped(next)
      onSignal?.({ liked, skipped: next, saved })
    } else {
      const next = !saved
      setSaved(next)
      onSignal?.({ liked, skipped, saved: next })
    }
  }

  return (
    <div style={railStyle}>
      <ActionBtn label="LIKE" icon="♥" active={liked} activeColor="var(--like-active)" onClick={() => toggle('like')} />
      <ActionBtn label="SKIP" icon="✕" active={skipped} activeColor="var(--skip-active)" onClick={() => toggle('skip')} />
      <ActionBtn label="SAVE" icon="🔖" active={saved} activeColor="var(--save-active)" onClick={() => toggle('save')} />
    </div>
  )
}

function ActionBtn({ label, icon, active, activeColor, onClick }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '56px', height: '56px',
        borderRadius: 'var(--radius-full)',
        background: hovered ? 'rgba(255,255,255,0.16)' : 'var(--action-btn-bg)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255,255,255,0.08)',
        cursor: 'pointer',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        transform: hovered ? 'scale(1.08)' : 'scale(1)',
        transition: 'transform 150ms, background 150ms',
        padding: 0,
      }}
    >
      <span style={{ fontSize: '22px', color: active ? activeColor : 'var(--text-muted)', lineHeight: 1 }}>
        {icon}
      </span>
      <span style={{
        fontFamily: "'Hanken Grotesk', sans-serif",
        fontSize: '10px', textTransform: 'uppercase',
        color: 'var(--text-dim)', marginTop: '4px', letterSpacing: '0.05em',
      }}>
        {label}
      </span>
    </button>
  )
}

const railStyle = {
  position: 'fixed', right: '16px', bottom: '100px',
  display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'center',
  zIndex: 50,
}
