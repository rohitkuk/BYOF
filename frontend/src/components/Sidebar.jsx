import { useState, useEffect } from 'react'
import { FilterPills } from './FilterPills'

export function Sidebar({ open, onClose, items, filters, onApply }) {
  const [local, setLocal] = useState(filters || {})

  useEffect(() => { setLocal(filters || {}) }, [filters])

  const sources = [...new Set((items || []).map(i => i.source).filter(Boolean))]

  const apply = () => {
    onApply(local)
    onClose()
  }

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div
          onClick={onClose}
          style={{
            position: 'fixed', inset: 0, zIndex: 199,
            background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          }}
        />
      )}

      {/* Drawer */}
      <div style={{
        position: 'fixed', top: 0, left: 0, height: '100vh',
        width: 'min(85vw, 340px)', background: 'var(--sidebar-bg)',
        zIndex: 200, overflowY: 'auto',
        transform: open ? 'translateX(0)' : 'translateX(-100%)',
        transition: '280ms cubic-bezier(0.4,0,0.2,1)',
        display: 'flex', flexDirection: 'column',
      }}>
        <div style={{ padding: '24px', flex: 1 }}>

          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <span style={{
              fontFamily: "'Playfair Display', Georgia, serif",
              fontSize: '22px', fontWeight: 700, color: 'var(--primary)',
            }}>
              BYOF
            </span>
            <button
              onClick={onClose}
              style={{
                width: '32px', height: '32px', borderRadius: '50%',
                background: 'var(--surface-high)', border: 'none',
                cursor: 'pointer', color: 'var(--text-muted)', fontSize: '18px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}
            >
              ×
            </button>
          </div>

          {/* Filters */}
          <FilterPills
            label="Category"
            options={['Technology', 'Science']}
            selected={local.category || null}
            onChange={v => setLocal(p => ({ ...p, category: v }))}
          />

          <FilterPills
            label="Date"
            options={['Today', 'This week', 'This month', 'All time']}
            selected={local.date || null}
            onChange={v => setLocal(p => ({ ...p, date: v }))}
          />

          <FilterPills
            label="Type"
            options={['Article', 'Newsletter', 'Paper']}
            selected={local.type || []}
            onChange={v => setLocal(p => ({ ...p, type: v }))}
            multiSelect
          />

          {sources.length > 0 && (
            <FilterPills
              label="Source"
              options={sources}
              selected={local.source || []}
              onChange={v => setLocal(p => ({ ...p, source: v }))}
              multiSelect
            />
          )}
        </div>

        {/* Apply button — sticky bottom */}
        <div style={{ padding: '0 24px 24px' }}>
          <button
            onClick={apply}
            style={{
              width: '100%', padding: '16px',
              background: 'var(--secondary)', color: 'var(--on-secondary)',
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontWeight: 600, fontSize: '14px',
              borderRadius: 'var(--radius-full)', border: 'none',
              cursor: 'pointer', letterSpacing: '0.05em',
            }}
          >
            Apply Filters
          </button>
        </div>
      </div>
    </>
  )
}
