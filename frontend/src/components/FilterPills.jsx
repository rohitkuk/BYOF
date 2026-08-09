export function FilterPills({ label, options, selected, onChange, multiSelect = false }) {
  const isSelected = (opt) =>
    multiSelect ? (selected || []).includes(opt) : selected === opt

  const handleClick = (opt) => {
    if (multiSelect) {
      const cur = selected || []
      const next = cur.includes(opt) ? cur.filter(o => o !== opt) : [...cur, opt]
      onChange(next)
    } else {
      onChange(selected === opt ? null : opt)
    }
  }

  return (
    <div style={{ marginBottom: '20px' }}>
      {label && (
        <p style={labelStyle}>{label}</p>
      )}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {options.map(opt => (
          <button
            key={opt}
            onClick={() => handleClick(opt)}
            style={isSelected(opt) ? activePillStyle : inactivePillStyle}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

const labelStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '11px', textTransform: 'uppercase',
  color: 'var(--text-dim)', letterSpacing: '0.1em',
  marginBottom: '8px',
}

const pillBase = {
  borderRadius: 'var(--radius-full)',
  padding: '8px 16px', fontSize: '14px',
  fontFamily: "'Hanken Grotesk', sans-serif",
  cursor: 'pointer', transition: 'background 150ms',
}

const activePillStyle = {
  ...pillBase,
  background: 'var(--secondary)', color: 'var(--on-secondary)', border: 'none',
}

const inactivePillStyle = {
  ...pillBase,
  background: 'transparent', border: '1.5px solid var(--outline-variant)',
  color: 'var(--text-muted)',
}
