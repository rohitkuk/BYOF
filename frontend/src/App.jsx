import { useState } from 'react'
import { useFeed } from './hooks/useFeed'
import { FeedCard } from './components/FeedCard'

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
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
    <>
      {/* Fixed top bar */}
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, pointerEvents: 'none' }}>
        <button
          style={fabStyle}
          onClick={() => setSidebarOpen(o => !o)}
        >
          ☰
        </button>
        <span style={wordmarkStyle}>BYOF</span>
      </div>

      {/* Scroll-snap feed */}
      <div style={feedStyle}>
        {items.map(item => (
          <FeedCard key={item.url} item={item} />
        ))}
      </div>
    </>
  )
}

const centerStyle = {
  height: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'var(--bg)',
}

const fabStyle = {
  position: 'absolute',
  top: '16px',
  left: '16px',
  width: '48px',
  height: '48px',
  borderRadius: '50%',
  background: 'var(--secondary)',
  border: 'none',
  cursor: 'pointer',
  color: 'var(--on-secondary)',
  fontSize: '20px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  pointerEvents: 'auto',
}

const wordmarkStyle = {
  position: 'absolute',
  top: '20px',
  right: '16px',
  fontFamily: "'Playfair Display', Georgia, serif",
  fontSize: '18px',
  fontWeight: 700,
  color: 'var(--primary)',
  letterSpacing: '0.1em',
  pointerEvents: 'auto',
}

const feedStyle = {
  height: '100vh',
  overflowY: 'scroll',
  scrollSnapType: 'y mandatory',
}
