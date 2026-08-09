export function ProgressDots({ total, current }) {
  return (
    <div style={containerStyle}>
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          style={{
            width: '3px',
            height: i === current ? '20px' : '5px',
            background: i === current ? 'var(--primary)' : 'var(--outline-variant)',
            borderRadius: '2px',
            transition: 'height 200ms, background 200ms',
          }}
        />
      ))}
    </div>
  )
}

const containerStyle = {
  position: 'fixed', left: '12px', top: '50%', transform: 'translateY(-50%)',
  display: 'flex', flexDirection: 'column', gap: '4px',
  zIndex: 50,
}
