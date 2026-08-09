export function FeedCard({ item }) {
  let domain = ''
  try {
    domain = new URL(item.url).hostname.replace('www.', '')
  } catch (_) {}
  const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`

  return (
    <section style={cardStyle}>
      {/* Background */}
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          style={{ position: 'absolute', width: '100%', height: '100%', objectFit: 'cover' }}
        />
      ) : (
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(135deg, #0b0f10, #1d2022, #272a2c)' }} />
      )}

      {/* Gradient overlay */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: '70%',
        background: 'linear-gradient(to top, rgba(11,15,16,0.96), rgba(11,15,16,0.5) 60%, transparent)',
      }} />

      {/* Content overlay */}
      <div style={{ position: 'absolute', bottom: '80px', left: '24px', right: '80px' }}>
        {/* Category pills */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {(item.categories || []).map(cat => (
            <span key={cat} style={pillStyle}>{cat}</span>
          ))}
        </div>

        {/* Title */}
        <h2 style={titleStyle}>{item.title}</h2>
      </div>

      {/* Meta bar */}
      <div style={metaBarStyle}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
          <img src={faviconUrl} alt="" style={{ width: '24px', height: '24px', borderRadius: '50%', flexShrink: 0 }} />
          <span style={sourceStyle}>{item.source}</span>
          <span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}&nbsp;·&nbsp;{item.read_time} min read</span>
        </div>
        <button onClick={() => window.open(item.url, '_blank')} style={readBtnStyle}>
          READ ↗
        </button>
      </div>
    </section>
  )
}

const cardStyle = {
  position: 'relative',
  height: '100vh',
  scrollSnapAlign: 'start',
  overflow: 'hidden',
  flexShrink: 0,
}

const pillStyle = {
  border: '1px solid var(--secondary)',
  color: 'var(--secondary)',
  background: 'rgba(147,207,235,0.12)',
  borderRadius: 'var(--radius-full)',
  padding: '4px 12px',
  fontSize: '11px',
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
}

const titleStyle = {
  fontFamily: "'Playfair Display', Georgia, serif",
  fontSize: '24px',
  fontWeight: 600,
  color: 'var(--text-primary)',
  lineHeight: 1.3,
  marginTop: '10px',
  display: '-webkit-box',
  WebkitLineClamp: 3,
  WebkitBoxOrient: 'vertical',
  overflow: 'hidden',
}

const metaBarStyle = {
  position: 'absolute',
  bottom: '20px',
  left: '24px',
  right: '80px',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: '8px',
}

const sourceStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '13px',
  fontWeight: 600,
  color: 'var(--text-primary)',
  whiteSpace: 'nowrap',
  flexShrink: 0,
}

const dimStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '13px',
  color: 'var(--text-dim)',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
}

const readBtnStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '12px',
  fontWeight: 600,
  color: 'var(--secondary)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  whiteSpace: 'nowrap',
  flexShrink: 0,
}
