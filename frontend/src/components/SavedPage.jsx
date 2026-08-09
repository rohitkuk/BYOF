import { useState } from 'react'

const TYPE_ICON = { Article: 'article', Newsletter: 'mail', Paper: 'description' }
const TYPE_FILTERS = ['All', 'Article', 'Newsletter', 'Paper']

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - d) / 1000)
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function SavedPage({ items }) {
  const [typeFilter, setTypeFilter] = useState('All')
  const [search, setSearch] = useState('')

  const filtered = items.filter(item => {
    const matchType = typeFilter === 'All' || item.type === typeFilter
    const matchSearch = !search || item.title?.toLowerCase().includes(search.toLowerCase())
    return matchType && matchSearch
  })

  return (
    <div style={{
      position: 'fixed',
      top: 'var(--top-bar-height)',
      bottom: 'var(--bottom-nav-height)',
      left: 0, right: 0,
      overflowY: 'auto',
      background: 'var(--bg)',
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 var(--container-padding)' }}>

        {/* Header */}
        <section style={{ paddingTop: '32px', paddingBottom: '32px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
            <h1 style={{
              fontFamily: "'Playfair Display', Georgia, serif",
              fontSize: '32px', fontWeight: 700,
              color: 'var(--text-primary)', letterSpacing: '-0.02em',
            }}>BYOF</h1>
            <p style={{
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontSize: '11px', fontWeight: 600,
              letterSpacing: '0.12em', textTransform: 'uppercase',
              color: 'var(--text-dim)', marginTop: '8px',
            }}>Saved Library</p>
          </div>

          {/* Search */}
          <div style={{ position: 'relative', maxWidth: '672px' }}>
            <span className="material-symbols-outlined" style={{
              position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)',
              fontSize: '20px', color: 'var(--outline)',
            }}>search</span>
            <input
              type="text"
              placeholder="Search your library..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                width: '100%',
                background: 'var(--surface-highest)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: 'var(--radius-full)',
                padding: '12px 16px 12px 48px',
                fontFamily: "'Hanken Grotesk', sans-serif",
                fontSize: '16px', color: 'var(--text-primary)',
                outline: 'none',
              }}
            />
          </div>
        </section>

        {/* Type filter pills */}
        <section style={{ marginBottom: '40px', overflowX: 'auto' }} className="no-scrollbar">
          <div style={{ display: 'flex', gap: '12px', width: 'max-content' }}>
            {TYPE_FILTERS.map(f => (
              <button
                key={f}
                onClick={() => setTypeFilter(f)}
                style={{
                  padding: '8px 24px',
                  borderRadius: 'var(--radius-full)',
                  border: f === typeFilter ? 'none' : '2px solid var(--tertiary)',
                  background: f === typeFilter ? 'var(--tertiary)' : 'transparent',
                  color: f === typeFilter ? 'var(--on-tertiary)' : 'var(--tertiary)',
                  fontFamily: "'Hanken Grotesk', sans-serif",
                  fontSize: '14px', fontWeight: 600, letterSpacing: '0.05em',
                  cursor: 'pointer',
                  transition: 'all 200ms',
                }}
              >
                {f}
              </button>
            ))}
          </div>
        </section>

        {/* Cards */}
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--outline-variant)', display: 'block', marginBottom: '16px' }}>bookmark</span>
            <p style={{
              fontFamily: "'Playfair Display', Georgia, serif",
              fontSize: '20px', color: 'var(--text-muted)', marginBottom: '8px',
            }}>
              {items.length === 0 ? 'Nothing saved yet' : 'No matches'}
            </p>
            <p style={{
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontSize: '14px', color: 'var(--text-dim)',
            }}>
              {items.length === 0 ? 'Tap the bookmark icon on any article to save it here.' : 'Try a different filter or search term.'}
            </p>
          </div>
        ) : (
          <section style={{ display: 'flex', flexDirection: 'column', gap: 'var(--gutter)', marginBottom: '48px' }}>
            {filtered.map(item => (
              <SavedCard key={item.url} item={item} />
            ))}
          </section>
        )}
      </div>
    </div>
  )
}

function SavedCard({ item }) {
  const type = item.type || 'Article'
  const icon = TYPE_ICON[type] || 'article'

  return (
    <article
      onClick={() => window.open(item.url, '_blank', 'noopener,noreferrer')}
      style={{
        background: 'var(--surface-low)',
        borderRadius: '16px',
        border: '1px solid rgba(255,255,255,0.08)',
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'background 200ms',
        display: 'flex', flexDirection: 'row', alignItems: 'center',
        gap: '16px', padding: '12px',
      }}
    >
      {/* Thumbnail */}
      <div style={{
        width: '96px', height: '96px',
        borderRadius: '12px', flexShrink: 0,
        overflow: 'hidden', position: 'relative',
        background: 'var(--surface-highest)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {item.image_url ? (
          <img
            src={item.image_url} alt=""
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={e => { e.target.style.display = 'none' }}
          />
        ) : (
          <span className="material-symbols-outlined" style={{ fontSize: '32px', color: 'var(--tertiary)' }}>{icon}</span>
        )}
        <div style={{
          position: 'absolute', top: '4px', left: '4px',
          background: 'rgba(105,212,244,0.15)',
          backdropFilter: 'blur(8px)',
          borderRadius: '9999px',
          padding: '2px 8px',
          fontFamily: "'Hanken Grotesk', sans-serif",
          fontSize: '10px', fontWeight: 600,
          letterSpacing: '0.08em', textTransform: 'uppercase',
          color: 'var(--tertiary)',
        }}>
          {type}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '12px', color: 'var(--text-dim)',
            overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
          }}>{item.source}</span>
          <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--outline-variant)', flexShrink: 0 }} />
          <span style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '12px', color: 'var(--text-dim)', flexShrink: 0,
          }}>{timeAgo(item.published_at)}</span>
        </div>
        <h3 style={{
          fontFamily: "'Playfair Display', Georgia, serif",
          fontSize: '18px', fontWeight: 500,
          color: 'var(--text-primary)', lineHeight: 1.3,
          display: '-webkit-box',
          WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}>
          {item.title}
        </h3>
      </div>

      <button
        onClick={e => e.stopPropagation()}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: '4px', color: 'var(--text-dim)', flexShrink: 0,
          transition: 'color 200ms',
        }}
        aria-label="More options"
      >
        <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>more_vert</span>
      </button>
    </article>
  )
}
