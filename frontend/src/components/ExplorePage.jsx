import { useState } from 'react'

const CONTENT_TYPES = ['Articles', 'Newsletters', 'Papers']
const TYPE_MAP = { Articles: 'Article', Newsletters: 'Newsletter', Papers: 'Paper' }

const TOPICS = [
  { label: 'Artificial Intelligence', category: 'Technology' },
  { label: 'Machine Learning',        category: 'Technology' },
  { label: 'Technology',              category: 'Technology' },
  { label: 'Research Papers',         category: 'Science' },
  { label: 'Science',                 category: 'Science' },
  { label: 'Deep Learning',           category: 'Technology' },
  { label: 'Programming',             category: 'Technology' },
  { label: 'Minimalism',              category: 'Technology' },
]

export function ExplorePage({ items, filters, onApply }) {
  const [selectedType, setSelectedType] = useState(
    filters.type?.length === 1
      ? Object.keys(TYPE_MAP).find(k => TYPE_MAP[k] === filters.type[0]) || null
      : null
  )
  const [selectedTopics, setSelectedTopics] = useState([])
  const [selectedSources, setSelectedSources] = useState(filters.source || [])

  const sources = [...new Set((items || []).map(i => i.source).filter(Boolean))]

  const toggleTopic = (topic) => {
    setSelectedTopics(prev =>
      prev.includes(topic.label)
        ? prev.filter(t => t !== topic.label)
        : [...prev, topic.label]
    )
  }

  const toggleSource = (src) => {
    setSelectedSources(prev =>
      prev.includes(src) ? prev.filter(s => s !== src) : [...prev, src]
    )
  }

  const handleApply = () => {
    const type = selectedType ? [TYPE_MAP[selectedType]] : []
    const topicCategories = [...new Set(
      TOPICS.filter(t => selectedTopics.includes(t.label)).map(t => t.category)
    )]
    onApply({
      type,
      category: topicCategories.length === 1 ? topicCategories[0] : null,
      source: selectedSources,
    })
  }

  const handleReset = () => {
    setSelectedType(null)
    setSelectedTopics([])
    setSelectedSources([])
    onApply({})
  }

  const sourceInitial = (src) => src.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

  const SOURCE_COLORS = {
    'Google News':      '#4285f4',
    'TechCrunch':       '#22c55e',
    'Papers with Code': '#f59e0b',
    'The Rundown AI':   '#8b5cf6',
    'MIT Technology Review': '#ef4444',
    'TLDR Tech':        '#06b6d4',
    'ArXiv':            '#f97316',
  }

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

        {/* ── Mobile header ── */}
        <div className="mobile-only" style={{ paddingTop: '32px', paddingBottom: '16px' }}>
          <h1 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: '32px', fontWeight: 700,
            color: 'var(--text-primary)', letterSpacing: '-0.02em',
            marginBottom: '8px',
          }}>Explore</h1>
          <p style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '16px', color: 'var(--text-muted)', lineHeight: 1.6,
          }}>Discover content that matters to you.</p>
        </div>

        {/* ── Desktop header ── */}
        <div className="desktop-only" style={{ paddingTop: '48px', paddingBottom: '32px' }}>
          <h1 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontSize: '64px', fontWeight: 700,
            color: 'var(--text-primary)', letterSpacing: '-0.02em',
            marginBottom: '16px',
          }}>Explore</h1>
          <p style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '18px', color: 'var(--text-muted)', lineHeight: 1.6,
            maxWidth: '640px',
          }}>Discover content that matters to you.</p>
        </div>

        {/* ── Main grid ── */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(12, 1fr)',
          gap: 'var(--gutter)',
          marginTop: '16px',
        }}>

          {/* Left column: type + topics */}
          <div style={{ gridColumn: 'span 12', display: 'flex', flexDirection: 'column', gap: '32px' }}
               className="explore-left">

            {/* Content Format segmented control */}
            <section>
              <h2 style={sectionLabelStyle}>Content Format</h2>
              <div style={{
                display: 'flex', padding: '4px',
                background: 'var(--surface-low)',
                borderRadius: 'var(--radius-full)',
                border: '1px solid rgba(255,255,255,0.05)',
                overflowX: 'auto',
              }} className="no-scrollbar">
                {/* "All" option */}
                <button
                  onClick={() => setSelectedType(null)}
                  style={{
                    flex: 1, padding: '8px 24px',
                    borderRadius: 'var(--radius-full)',
                    border: 'none', cursor: 'pointer',
                    fontFamily: "'Hanken Grotesk', sans-serif",
                    fontSize: '14px', fontWeight: 600, letterSpacing: '0.05em',
                    whiteSpace: 'nowrap',
                    transition: 'all 300ms',
                    ...(selectedType === null
                      ? { background: 'var(--primary-container)', color: 'var(--on-primary-container)', boxShadow: '0 0 15px rgba(105,212,244,0.25)' }
                      : { background: 'none', color: 'var(--text-muted)' }),
                  }}
                >
                  All
                </button>
                {CONTENT_TYPES.map(t => (
                  <button
                    key={t}
                    onClick={() => setSelectedType(selectedType === t ? null : t)}
                    style={{
                      flex: 1, padding: '8px 24px',
                      borderRadius: 'var(--radius-full)',
                      border: 'none', cursor: 'pointer',
                      fontFamily: "'Hanken Grotesk', sans-serif",
                      fontSize: '14px', fontWeight: 600, letterSpacing: '0.05em',
                      whiteSpace: 'nowrap',
                      transition: 'all 300ms',
                      ...(selectedType === t
                        ? { background: 'var(--primary-container)', color: 'var(--on-primary-container)', boxShadow: '0 0 15px rgba(105,212,244,0.25)' }
                        : { background: 'none', color: 'var(--text-muted)' }),
                    }}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </section>

            {/* Topics of Interest */}
            <section>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={sectionLabelStyle}>Topics of Interest</h2>
                {selectedTopics.length > 0 && (
                  <button
                    onClick={() => setSelectedTopics([])}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer',
                      fontFamily: "'Hanken Grotesk', sans-serif",
                      fontSize: '12px', color: 'var(--tertiary)',
                    }}
                  >
                    Clear All
                  </button>
                )}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                {TOPICS.map(topic => {
                  const active = selectedTopics.includes(topic.label)
                  return (
                    <button
                      key={topic.label}
                      onClick={() => toggleTopic(topic)}
                      className="spring"
                      style={{
                        padding: '8px 24px',
                        borderRadius: 'var(--radius-full)',
                        border: active ? '2px solid var(--tertiary)' : '1px solid var(--outline-variant)',
                        background: active ? 'rgba(105,212,244,0.10)' : 'var(--surface-lowest)',
                        color: active ? 'var(--tertiary)' : 'var(--text-muted)',
                        fontFamily: "'Hanken Grotesk', sans-serif",
                        fontSize: '16px', cursor: 'pointer',
                        transition: 'all 0.4s cubic-bezier(0.175,0.885,0.32,1.275)',
                      }}
                    >
                      {topic.label}
                    </button>
                  )
                })}
              </div>
            </section>
          </div>

          {/* Right column: sources */}
          <div style={{ gridColumn: 'span 12', marginTop: '8px' }} className="explore-right">
            <div style={{
              background: 'var(--surface-lowest)',
              borderRadius: 'var(--radius)',
              border: '1px solid rgba(255,255,255,0.08)',
              padding: '24px',
              display: 'flex', flexDirection: 'column',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={sectionLabelStyle}>Preferred Sources</h2>
                <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--text-dim)' }}>search</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {sources.length === 0 ? (
                  <p style={{ fontFamily: "'Hanken Grotesk', sans-serif", fontSize: '14px', color: 'var(--text-dim)', textAlign: 'center', padding: '16px 0' }}>
                    No sources loaded yet. Refresh the feed first.
                  </p>
                ) : sources.map(src => {
                  const active = selectedSources.includes(src)
                  const color = SOURCE_COLORS[src] || '#909098'
                  return (
                    <label
                      key={src}
                      onClick={() => toggleSource(src)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: '16px',
                        padding: '12px',
                        borderRadius: 'var(--radius)',
                        border: active ? '1px solid rgba(70,70,77,0.3)' : '1px solid transparent',
                        background: active ? 'var(--bg)' : 'none',
                        cursor: 'pointer',
                        transition: 'all 200ms',
                      }}
                    >
                      <div style={{
                        width: '40px', height: '40px', borderRadius: '50%', flexShrink: 0,
                        background: color,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontFamily: "'Hanken Grotesk', sans-serif",
                        fontSize: '13px', fontWeight: 700, color: '#fff',
                      }}>
                        {sourceInitial(src)}
                      </div>
                      <span style={{
                        fontFamily: "'Hanken Grotesk', sans-serif",
                        fontSize: '16px', flex: 1,
                        color: active ? 'var(--text-primary)' : 'var(--text-muted)',
                      }}>
                        {src}
                      </span>
                      <div style={{
                        width: '24px', height: '24px', borderRadius: '50%', flexShrink: 0,
                        border: active ? '2px solid var(--tertiary)' : '2px solid var(--outline-variant)',
                        background: active ? 'var(--tertiary)' : 'none',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        transition: 'all 200ms',
                      }}>
                        {active && (
                          <span className="material-symbols-outlined icon-filled" style={{ fontSize: '14px', color: 'var(--bg)' }}>check</span>
                        )}
                      </div>
                    </label>
                  )
                })}
              </div>

              {sources.length > 0 && (
                <button
                  style={{
                    marginTop: '24px', width: '100%', padding: '8px',
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontFamily: "'Hanken Grotesk', sans-serif",
                    fontSize: '14px', color: 'var(--tertiary)',
                    transition: 'opacity 200ms',
                  }}
                  onClick={() => setSelectedSources(selectedSources.length === sources.length ? [] : [...sources])}
                >
                  {selectedSources.length === sources.length ? 'Deselect All' : 'Select All Sources'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ── CTA area ── */}
        <div style={{
          display: 'flex', gap: '12px',
          justifyContent: 'flex-end',
          padding: '24px 0 32px',
          flexWrap: 'wrap',
        }}>
          <button
            onClick={handleReset}
            style={{
              padding: '16px 32px',
              background: 'none',
              border: '1px solid var(--outline-variant)',
              color: 'var(--text-muted)',
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontWeight: 600, fontSize: '14px', letterSpacing: '0.05em',
              borderRadius: 'var(--radius-full)', cursor: 'pointer',
              transition: 'all 200ms',
            }}
          >
            Reset
          </button>
          <button
            onClick={handleApply}
            style={{
              padding: '16px 48px',
              background: 'var(--tertiary)',
              border: 'none',
              color: 'var(--on-tertiary)',
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontWeight: 600, fontSize: '14px', letterSpacing: '0.05em',
              borderRadius: 'var(--radius-full)', cursor: 'pointer',
              boxShadow: '0 0 20px rgba(105,212,244,0.2)',
              transition: 'all 200ms',
            }}
          >
            Apply Filters
          </button>
        </div>

      </div>
    </div>
  )
}

const sectionLabelStyle = {
  fontFamily: "'Hanken Grotesk', sans-serif",
  fontSize: '11px', fontWeight: 600,
  letterSpacing: '0.12em', textTransform: 'uppercase',
  color: 'var(--text-dim)',
  marginBottom: '24px',
}
