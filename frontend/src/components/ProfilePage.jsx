import { usePreferences } from '../hooks/usePreferences'

const STAT_ITEMS = [
  { icon: 'auto_awesome', label: 'Articles Read', value: '—' },
  { icon: 'bookmark',     label: 'Saved',         value: '—' },
  { icon: 'favorite',     label: 'Liked',          value: '—' },
]

export function ProfilePage() {
  const { preferences, loading } = usePreferences()

  const cats = preferences?.categories || []
  const subcats = preferences?.subcategories || []

  return (
    <div style={{
      position: 'fixed',
      top: 'var(--top-bar-height)',
      bottom: 'var(--bottom-nav-height)',
      left: 0, right: 0,
      overflowY: 'auto',
      background: 'var(--bg)',
    }}>
      <div style={{
        maxWidth: '1280px', margin: '0 auto',
        padding: '0 var(--container-padding)',
        display: 'flex', flexDirection: 'column',
        gap: '32px',
        paddingTop: '32px', paddingBottom: '48px',
      }}>

        {/* Avatar + name */}
        <section style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '16px', paddingBottom: '16px' }}>
          <div style={{ position: 'relative', marginBottom: '16px' }}>
            <div style={{
              width: '96px', height: '96px', borderRadius: '50%',
              background: 'var(--surface-high)',
              border: '2px solid rgba(191,197,228,0.2)',
              boxShadow: '0 0 20px rgba(105,212,244,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--primary)' }}>person</span>
            </div>
            <button style={{
              position: 'absolute', bottom: 0, right: 0,
              width: '28px', height: '28px', borderRadius: '50%',
              background: 'var(--primary-container)',
              border: '1px solid rgba(255,255,255,0.1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer',
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--primary)' }}>edit</span>
            </button>
          </div>
          <h2 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: '24px', fontWeight: 500, color: 'var(--text-primary)',
          }}>BYOF User</h2>
          <p style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '14px', color: 'var(--text-dim)', marginTop: '4px',
          }}>Local-first · Private by design</p>
        </section>

        {/* Stats row */}
        <section style={{
          display: 'flex', gap: 'var(--gutter)',
          background: 'var(--surface-low)',
          borderRadius: 'var(--radius)',
          border: '1px solid rgba(255,255,255,0.06)',
          padding: '24px',
        }}>
          {STAT_ITEMS.map(s => (
            <div key={s.label} style={{
              flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px',
            }}>
              <span className="material-symbols-outlined" style={{ fontSize: '24px', color: 'var(--text-dim)' }}>{s.icon}</span>
              <span style={{
                fontFamily: "'Playfair Display', Georgia, serif",
                fontSize: '22px', fontWeight: 600, color: 'var(--text-primary)',
              }}>{s.value}</span>
              <span style={{
                fontFamily: "'Hanken Grotesk', sans-serif",
                fontSize: '11px', color: 'var(--text-dim)',
                textTransform: 'uppercase', letterSpacing: '0.08em',
              }}>{s.label}</span>
            </div>
          ))}
        </section>

        {/* Preferences summary */}
        <section style={{
          background: 'var(--surface-lowest)',
          borderRadius: 'var(--radius)',
          border: '1px solid rgba(255,255,255,0.06)',
          padding: '24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={sectionLabel}>Reading Preferences</h3>
            <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--text-dim)' }}>tune</span>
          </div>

          {loading ? (
            <p style={{ fontFamily: "'Hanken Grotesk', sans-serif", fontSize: '14px', color: 'var(--text-dim)' }}>Loading…</p>
          ) : cats.length === 0 ? (
            <p style={{ fontFamily: "'Hanken Grotesk', sans-serif", fontSize: '14px', color: 'var(--text-dim)' }}>
              No preferences set yet. Preferences are configured via <code style={{ color: 'var(--tertiary)', background: 'var(--surface-high)', padding: '2px 6px', borderRadius: '4px' }}>preferences.json</code>.
            </p>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {[...cats, ...subcats].map(tag => (
                <span key={tag} style={{
                  padding: '6px 16px',
                  borderRadius: 'var(--radius-full)',
                  border: '1px solid var(--outline-variant)',
                  fontFamily: "'Hanken Grotesk', sans-serif",
                  fontSize: '13px', color: 'var(--text-muted)',
                }}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </section>

        {/* App info */}
        <section style={{
          background: 'var(--surface-low)',
          borderRadius: 'var(--radius)',
          border: '1px solid rgba(255,255,255,0.06)',
          padding: '24px',
          display: 'flex', flexDirection: 'column', gap: '16px',
        }}>
          <h3 style={sectionLabel}>About BYOF</h3>
          {[
            { icon: 'devices',         label: 'Local-first',    desc: 'All data stays on your device' },
            { icon: 'lock',            label: 'Private',        desc: 'No telemetry, no analytics' },
            { icon: 'rss_feed',        label: 'Open sources',   desc: 'Google News, TechCrunch, Papers with Code, The Rundown AI' },
          ].map(row => (
            <div key={row.label} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                background: 'var(--surface-high)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: '20px', color: 'var(--secondary)' }}>{row.icon}</span>
              </div>
              <div>
                <p style={{
                  fontFamily: "'Hanken Grotesk', sans-serif",
                  fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)',
                }}>{row.label}</p>
                <p style={{
                  fontFamily: "'Hanken Grotesk', sans-serif",
                  fontSize: '13px', color: 'var(--text-dim)',
                }}>{row.desc}</p>
              </div>
            </div>
          ))}
        </section>

      </div>
    </div>
  )
}

const sectionLabel = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '11px', fontWeight: 600,
  letterSpacing: '0.12em', textTransform: 'uppercase',
  color: 'var(--text-dim)',
}
