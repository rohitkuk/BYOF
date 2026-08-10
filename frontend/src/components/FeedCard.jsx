import { useState } from 'react'

export function FeedCard({ item, skipped = false, cardRef }) {
  const [opening, setOpening] = useState(false)

  let domain = ''
  try { domain = new URL(item.url).hostname.replace('www.', '') } catch (_) {}
  const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`

  const openLink = (e) => {
    e.stopPropagation()
    setOpening(true)
    setTimeout(() => {
      window.open(item.url, '_blank', 'noopener,noreferrer')
      setOpening(false)
    }, 180)
  }

  return (
    <section
      ref={cardRef}
      style={cardStyle}
    >
      {/* Background image or fallback gradient */}
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          onError={e => { e.target.style.display = 'none' }}
        />
      ) : (
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, #0b0f10, #1d2022, #272a2c)' }} />
      )}

      {/* Skip overlay */}
      {skipped && (
        <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.45)', zIndex: 5 }} />
      )}

      {/* Vignette */}
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.15)' }} />

      {/* Gradient overlay — bottom to top */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: '75%',
        background: 'linear-gradient(to top, rgba(10,17,40,0.97), rgba(10,17,40,0.55) 55%, transparent)',
      }} />

      {/* Content overlay — category + title */}
      <div style={{
        position: 'absolute',
        bottom: 'calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 72px)',
        left: '24px', right: '80px',
        zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
          {(item.categories || []).map(cat => (
            <span key={cat} style={pillStyle}>{cat}</span>
          ))}
          {item.read_time && (
            <span style={{ ...pillStyle, background: 'none', border: 'none', color: 'var(--text-dim)', letterSpacing: '0.08em', fontSize: '11px' }}>
              {item.read_time} MIN READ
            </span>
          )}
        </div>
        <h2
          onClick={openLink}
          style={{
            ...titleStyle,
            cursor: 'pointer',
            opacity: opening ? 0.55 : 1,
            transform: opening ? 'scale(0.985)' : 'scale(1)',
            transition: 'opacity 180ms ease, transform 180ms ease',
          }}
        >{item.title}</h2>
      </div>

      {/* Meta bar — source + read button */}
      <div style={{
        position: 'absolute',
        bottom: 'calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 14px)',
        left: '24px', right: '80px',
        zIndex: 10,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', minWidth: 0 }}>
          <img
            src={faviconUrl} alt=""
            style={{ width: '24px', height: '24px', borderRadius: '50%', flexShrink: 0 }}
            onError={e => { e.target.style.display = 'none' }}
          />
          <span style={sourceStyle}>{item.source}</span>
          <span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}</span>
        </div>
        <button
          onClick={openLink}
          style={{
            ...readBtnStyle,
            opacity: opening ? 0.55 : 1,
            transition: 'opacity 180ms ease',
          }}
        >
          READ ↗
        </button>
      </div>
    </section>
  )
}

const cardStyle = {
  position: 'relative',
  height: '100dvh',
  scrollSnapAlign: 'start',
  overflow: 'hidden',
  flexShrink: 0,
}

const pillStyle = {
  border: '1px solid rgba(147,207,235,0.5)',
  color: 'var(--secondary)',
  background: 'rgba(147,207,235,0.12)',
  backdropFilter: 'blur(8px)',
  borderRadius: 'var(--radius-full)',
  padding: '4px 14px',
  fontSize: '11px',
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
}

const titleStyle = {
  fontFamily: "'Playfair Display', Georgia, serif",
  fontSize: '24px',
  fontWeight: 600,
  color: 'var(--text-primary)',
  lineHeight: 1.3,
  display: '-webkit-box',
  WebkitLineClamp: 3,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
  textShadow: '0 1px 4px rgba(0,0,0,0.5)',
}

const sourceStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '13px', fontWeight: 600,
  color: 'var(--text-primary)',
  whiteSpace: 'nowrap', flexShrink: 0,
}

const dimStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '13px', color: 'var(--text-dim)',
  whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
}

const readBtnStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '12px', fontWeight: 600,
  color: 'var(--secondary)',
  textTransform: 'uppercase', letterSpacing: '0.05em',
  background: 'none', border: 'none',
  cursor: 'pointer', whiteSpace: 'nowrap', flexShrink: 0,
  padding: 0,
}
