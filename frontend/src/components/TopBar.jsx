const VIEW_LABELS = { feed: 'For You', explore: 'Explore', saved: 'Saved', profile: 'Profile' }

export function TopBar({ view, onNavigate }) {
  return (
    <>
      {/* ── Mobile top bar ── */}
      <header
        className="mobile-only"
        style={{
          position: 'fixed', top: 0, left: 0, right: 0,
          height: 'var(--top-bar-height)', zIndex: 50,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 16px',
          background: 'rgba(16,20,21,0.85)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <button
          onClick={() => onNavigate('feed')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          <h1 style={wordmarkStyle}>BYOF</h1>
        </button>

        <button
          onClick={() => onNavigate('profile')}
          aria-label="Profile"
          style={avatarBtnStyle}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '20px', color: 'var(--text-muted)' }}>person</span>
        </button>
      </header>

      {/* ── Desktop top bar ── */}
      <header
        className="desktop-only"
        style={{
          position: 'fixed', top: 0, left: 0, right: 0,
          height: 'var(--top-bar-height)', zIndex: 50,
          background: 'rgba(16,20,21,0.85)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <div style={{
          maxWidth: '1280px', margin: '0 auto',
          height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0 var(--container-padding)',
        }}>
        <div>
          <button
            onClick={() => onNavigate('feed')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          >
            <h1 style={wordmarkStyle}>BYOF</h1>
          </button>
        </div>

        {/* Center: nav links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
          {(['feed', 'explore', 'saved', 'profile']).map(v => {
            const isActive = view === v
            return (
              <button
                key={v}
                onClick={() => onNavigate(v)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '6px',
                  background: 'none', border: 'none', cursor: 'pointer',
                  padding: '4px 0',
                  fontFamily: "'Hanken Grotesk', sans-serif",
                  fontSize: '14px', fontWeight: 600,
                  letterSpacing: '0.05em',
                  color: isActive ? 'var(--primary)' : 'var(--text-dim)',
                  borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
                  transition: 'color 200ms, border-color 200ms',
                }}
              >
                {v === 'explore' && (
                  <span
                    className={`material-symbols-outlined ${isActive ? 'icon-filled' : ''}`}
                    style={{ fontSize: '16px' }}
                  >
                    explore
                  </span>
                )}
                {VIEW_LABELS[v]}
              </button>
            )
          })}
        </nav>

        {/* Right: avatar */}
        <button
          onClick={() => onNavigate('profile')}
          aria-label="Profile"
          style={avatarBtnStyle}
        >
          <span className="material-symbols-outlined" style={{ fontSize: '20px', color: 'var(--text-muted)' }}>person</span>
        </button>
        </div>
      </header>
    </>
  )
}

const wordmarkStyle = {
  fontFamily: "'Playfair Display', Georgia, serif",
  fontSize: '20px', fontWeight: 700,
  color: 'var(--primary)',
  letterSpacing: '0.08em',
}

const avatarBtnStyle = {
  width: '40px', height: '40px', borderRadius: '50%',
  background: 'var(--surface-high)',
  border: '1px solid var(--outline-variant)',
  cursor: 'pointer',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  transition: 'opacity 200ms',
  flexShrink: 0,
}
