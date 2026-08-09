const TABS = [
  { view: 'feed',    label: 'For You', icon: 'auto_awesome' },
  { view: 'explore', label: 'Explore', icon: 'explore' },
  { view: 'saved',   label: 'Saved',   icon: 'bookmark' },
  { view: 'profile', label: 'Profile', icon: 'person' },
]

export function BottomNav({ view, onNavigate }) {
  return (
    <nav
      className="mobile-only"
      style={{
        position: 'fixed', bottom: 0, left: 0, right: 0,
        height: 'var(--bottom-nav-height)', zIndex: 50,
        display: 'flex', alignItems: 'center', justifyContent: 'space-around',
        padding: '8px 16px 20px',
        background: 'rgba(29,32,34,0.92)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        borderRadius: '16px 16px 0 0',
      }}
    >
      {TABS.map(tab => {
        const isActive = view === tab.view
        return (
          <button
            key={tab.view}
            onClick={() => onNavigate(tab.view)}
            aria-label={tab.label}
            style={{
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              gap: '2px',
              background: isActive ? 'var(--secondary-container)' : 'none',
              border: 'none', cursor: 'pointer',
              padding: '6px 20px',
              borderRadius: '9999px',
              transition: 'all 300ms cubic-bezier(0.4,0,0.2,1)',
            }}
          >
            <div style={{ position: 'relative' }}>
              <span
                className={`material-symbols-outlined ${isActive ? 'icon-filled' : ''}`}
                style={{
                  fontSize: '24px',
                  color: isActive ? 'var(--on-secondary-container)' : 'var(--text-dim)',
                  display: 'block',
                }}
              >
                {tab.icon}
              </span>
              {isActive && (
                <div style={{
                  position: 'absolute', bottom: '-3px',
                  left: '50%', transform: 'translateX(-50%)',
                  width: '4px', height: '4px',
                  borderRadius: '50%',
                  background: 'var(--secondary)',
                }} />
              )}
            </div>
            <span style={{
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontSize: '10px', fontWeight: 600,
              letterSpacing: '0.05em',
              color: isActive ? 'var(--on-secondary-container)' : 'var(--text-dim)',
              marginTop: '2px',
            }}>
              {tab.label}
            </span>
          </button>
        )
      })}
    </nav>
  )
}
