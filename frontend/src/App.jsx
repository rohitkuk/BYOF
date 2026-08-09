import { useFeed } from './hooks/useFeed'

export default function App() {
  const { items, loading, error } = useFeed()

  if (loading) {
    return (
      <div style={centerStyle}>
        <p style={{ fontFamily: "'Hanken Grotesk', sans-serif", color: 'var(--text-muted)', fontSize: '16px' }}>
          Loading your feed...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={centerStyle}>
        <p style={{ fontFamily: "'Hanken Grotesk', sans-serif", color: 'var(--secondary)', fontSize: '16px' }}>
          Could not load feed. Is api.py running?
        </p>
      </div>
    )
  }

  return (
    <div style={centerStyle}>
      <h1 style={{
        fontFamily: "'Playfair Display', Georgia, serif",
        color: 'var(--text-primary)',
        fontSize: '40px',
        fontWeight: 700,
        letterSpacing: '0.05em',
      }}>
        {items.length} items loaded
      </h1>
    </div>
  )
}

const centerStyle = {
  height: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'var(--bg)',
}
