import { useState, useMemo } from 'react'

export function FeedCard({ item, skipped = false, cardRef, index = 0, loadImage = false }) {
  const [opening, setOpening] = useState(false)
  const [showSummary, setShowSummary] = useState(false)

  const { domain, faviconUrl } = useMemo(() => {
    let domain = ''
    try { domain = new URL(item.url).hostname.replace('www.', '') } catch (_) {}
    return { domain, faviconUrl: `https://www.google.com/s2/favicons?domain=${domain}&sz=32` }
  }, [item.url])

  const openLink = (e) => {
    e.stopPropagation()
    setShowSummary(false)
    setOpening(true)
    setTimeout(() => {
      window.open(item.url, '_blank', 'noopener,noreferrer')
      setOpening(false)
    }, 700)
  }

  return (
    <section
      ref={cardRef}
      data-card-index={index}
      style={cardStyle}
    >
      {/* Background: only mount <img> when within the active window */}
      {item.image_url && loadImage ? (
        <img
          src={item.image_url}
          alt=""
          decoding="async"
          fetchpriority={index === 0 ? 'high' : 'auto'}
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

      {/* Opening in new tab overlay */}
      {opening && (
        <div style={openingOverlayStyle}>
          <span style={openingTextStyle}>Opening in a new tab&nbsp;&nbsp;↗</span>
          <div style={openingSpinnerStyle} />
        </div>
      )}

      {/* Summary panel */}
      {showSummary && (
        <div style={summaryPanelStyle} onClick={() => setShowSummary(false)}>
          <p style={summaryTextStyle}>{item.summary}</p>
        </div>
      )}

      {/* Content overlay — category + keywords + title */}
      <div style={{
        position: 'absolute',
        bottom: 'calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 72px)',
        left: '24px', right: '80px',
        zIndex: 10,
      }}>
        {/* Category pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '8px' }}>
          {(item.categories || []).map(cat => (
            <span key={cat} style={pillStyle}>{cat}</span>
          ))}
          {item.read_time && (
            <span style={{ ...pillStyle, background: 'none', border: 'none', color: 'var(--text-dim)', letterSpacing: '0.08em', fontSize: '11px' }}>
              {item.read_time} MIN READ
            </span>
          )}
        </div>

        {/* Keyword pills */}
        {(item.keywords || []).length > 0 && (
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
            {item.keywords.slice(0, 5).map(kw => (
              <span key={kw} style={keywordPillStyle}>{kw}</span>
            ))}
          </div>
        )}

        {/* Title */}
        <h2
          onClick={openLink}
          style={{ ...titleStyle, cursor: 'pointer' }}
        >{item.title}</h2>
      </div>

      {/* Meta bar — source + summary + read button */}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0', flexShrink: 0 }}>
          {item.summary && (
            <button
              onClick={e => { e.stopPropagation(); setShowSummary(s => !s) }}
              style={{
                ...readBtnStyle,
                marginRight: '16px',
                color: showSummary ? 'var(--text-primary)' : 'var(--text-dim)',
              }}
            >
              {showSummary ? 'CLOSE ✕' : 'SUMMARY'}
            </button>
          )}
          <button
            onClick={openLink}
            style={readBtnStyle}
          >
            READ ↗
          </button>
        </div>
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

const keywordPillStyle = {
  border: '1px solid rgba(255,255,255,0.12)',
  color: 'var(--text-dim)',
  background: 'rgba(255,255,255,0.06)',
  backdropFilter: 'blur(6px)',
  borderRadius: 'var(--radius-full)',
  padding: '3px 10px',
  fontSize: '10px',
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontWeight: 500,
  textTransform: 'lowercase',
  letterSpacing: '0.04em',
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

const summaryPanelStyle = {
  position: 'absolute',
  bottom: 'calc(var(--bottom-nav-height) + env(safe-area-inset-bottom, 0px) + 110px)',
  left: '24px', right: '24px',
  zIndex: 15,
  background: 'rgba(10,17,40,0.92)',
  backdropFilter: 'blur(20px)',
  borderRadius: '16px',
  border: '1px solid rgba(147,207,235,0.15)',
  padding: '16px 20px',
  animation: 'byof-fadein 220ms ease',
  cursor: 'pointer',
}

const summaryTextStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '14px',
  lineHeight: 1.6,
  color: 'var(--text-primary)',
  margin: 0,
}

const openingOverlayStyle = {
  position: 'absolute', inset: 0, zIndex: 30,
  background: 'rgba(10,17,40,0.82)',
  backdropFilter: 'blur(12px)',
  display: 'flex', flexDirection: 'column',
  alignItems: 'center', justifyContent: 'center', gap: '20px',
  animation: 'byof-fadein 250ms ease',
}

const openingTextStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '18px', fontWeight: 600,
  color: 'var(--text-primary)',
  letterSpacing: '0.02em',
}

const openingSpinnerStyle = {
  width: '24px', height: '24px',
  border: '2px solid rgba(147,207,235,0.2)',
  borderTopColor: 'var(--secondary)',
  borderRadius: '50%',
  animation: 'spin 700ms linear infinite',
}
