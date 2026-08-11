import { useState, useEffect, useRef, useCallback } from 'react'
import { useFeed } from './hooks/useFeed'
import { FeedCard } from './components/FeedCard'
import { ActionRail } from './components/ActionRail'
import { ProgressDots } from './components/ProgressDots'
import { TopBar } from './components/TopBar'
import { BottomNav } from './components/BottomNav'
import { ExplorePage } from './components/ExplorePage'
import { SavedPage } from './components/SavedPage'
import { ProfilePage } from './components/ProfilePage'
import { LandingPage } from './components/LandingPage'

export default function App() {
  const [signedIn, setSignedIn] = useState(
    () => !!localStorage.getItem('byof_signed_in')
  )
  const [view, setView] = useState('feed')
  const [activeIndex, setActiveIndex] = useState(0)
  const [signals, setSignals] = useState({})
  const [filters, setFilters] = useState({})

  // All hooks must be called unconditionally — before any early return
  const { items, loading, error } = useFeed(filters)
  const cardRefs = useRef([])

  useEffect(() => {
    if (!items.length) return
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const i = parseInt(entry.target.dataset.cardIndex, 10)
            if (!isNaN(i)) setActiveIndex(i)
          }
        })
      },
      { threshold: 0.5 }
    )
    cardRefs.current.forEach(el => { if (el) obs.observe(el) })
    return () => obs.disconnect()
  }, [items])

  const handleSignal = useCallback((url, state) => {
    setSignals(prev => ({ ...prev, [url]: state }))
  }, [])

  const handleApplyFilters = useCallback((newFilters) => {
    setFilters(newFilters)
    setView('feed')
  }, [])

  const handleSignIn = () => {
    localStorage.setItem('byof_signed_in', '1')
    setSignedIn(true)
  }

  if (!signedIn) {
    return <LandingPage onSignIn={handleSignIn} />
  }

  const savedItems = items.filter(i => signals[i.url]?.saved)
  const activeItem = items[activeIndex]

  return (
    <>
      <TopBar view={view} onNavigate={setView} />

      {/* ── Feed view ── */}
      {view === 'feed' && (
        <>
          {loading && (
            <div style={centerStyle}>
              <div style={spinnerStyle} />
              <p style={statusTextStyle}>Loading your feed…</p>
            </div>
          )}

          {error && !loading && (
            <div style={centerStyle}>
              <span className="material-symbols-outlined" style={{ fontSize: '40px', color: 'var(--outline-variant)', marginBottom: '16px' }}>wifi_off</span>
              <p style={statusTextStyle}>Could not load feed.</p>
              <p style={{ ...statusTextStyle, fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Is <code style={{ color: 'var(--tertiary)' }}>api.py</code> running on :8000?
              </p>
            </div>
          )}

          {!loading && !error && items.length > 0 && (
            <>
              <ProgressDots total={items.length} current={activeIndex} />
              {activeItem && (
                <ActionRail
                  key={activeItem.url}
                  item={activeItem}
                  onSignal={state => handleSignal(activeItem.url, state)}
                />
              )}
              <div style={feedStyle}>
                {items.map((item, i) => (
                  <FeedCard
                    key={item.url}
                    item={item}
                    index={i}
                    loadImage={i >= activeIndex - 1 && i <= activeIndex + 3}
                    skipped={signals[item.url]?.skipped}
                    cardRef={el => { cardRefs.current[i] = el }}
                  />
                ))}
              </div>
            </>
          )}

          {!loading && !error && items.length === 0 && (
            <div style={centerStyle}>
              <span className="material-symbols-outlined" style={{ fontSize: '40px', color: 'var(--outline-variant)', marginBottom: '16px' }}>inbox</span>
              <p style={statusTextStyle}>No articles yet.</p>
              <p style={{ ...statusTextStyle, fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Run <code style={{ color: 'var(--tertiary)' }}>uv run python app.py</code> to fetch content.
              </p>
            </div>
          )}
        </>
      )}

      {/* ── Explore view ── */}
      {view === 'explore' && (
        <ExplorePage items={items} filters={filters} onApply={handleApplyFilters} />
      )}

      {/* ── Saved view ── */}
      {view === 'saved' && (
        <SavedPage items={savedItems} />
      )}

      {/* ── Profile view ── */}
      {view === 'profile' && (
        <ProfilePage />
      )}

      <BottomNav view={view} onNavigate={setView} />
    </>
  )
}

const feedStyle = {
  position: 'fixed', inset: 0,
  overflowY: 'scroll',
  scrollSnapType: 'y mandatory',
  zIndex: 0,
}

const centerStyle = {
  position: 'fixed', inset: 0,
  display: 'flex', flexDirection: 'column',
  alignItems: 'center', justifyContent: 'center',
  background: 'var(--bg)',
  zIndex: 1,
}

const statusTextStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '16px', color: 'var(--text-muted)',
}

const spinnerStyle = {
  width: '32px', height: '32px',
  border: '3px solid var(--outline-variant)',
  borderTopColor: 'var(--secondary)',
  borderRadius: '50%',
  animation: 'spin 700ms linear infinite',
  marginBottom: '16px',
}
