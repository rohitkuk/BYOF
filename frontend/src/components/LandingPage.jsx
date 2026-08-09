import { useState } from 'react'

export function LandingPage({ onSignIn }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div style={{
      position: 'relative',
      height: '100vh',
      overflow: 'hidden',
      background: '#0a1128',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '0 24px',
    }}>

      {/* Ambient background image */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden' }}>
        <img
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuCPVlTgf_J5YXxZbIdA6zylbAU8rNHSMNDstF7XNzNfBBxPhi0F4i6Z7UvkC-UqTpX57AzDNGBBSgOCo1aghhLNpDWXZ0kaAFuD9EEEEhYsufUnPwfNOjOx22xnFTuZQrIvVxRb91dHECa40DWHV0UJquZ0Cf5HPn4PmPaRJWZ2UioQmqrhwiMmeu6mROTt90T3QdbXojCxB3i_Y1f0cKG4KpLY243fTyLmuygGyoM7NQbGRpAlmeYqmQ"
          alt=""
          aria-hidden="true"
          style={{
            width: '100%', height: '100%',
            objectFit: 'cover',
            opacity: 0.30,
            mixBlendMode: 'overlay',
          }}
        />
        {/* Gradient overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(to top, #0a1128, rgba(10,17,40,0.80) 50%, transparent)',
        }} />
      </div>

      {/* Header — BYOF wordmark */}
      <header style={{
        position: 'absolute', top: 0, left: 0, right: 0,
        padding: '24px',
        zIndex: 20,
        display: 'flex', justifyContent: 'center',
      }}>
        <div style={{ maxWidth: '1280px', width: '100%', display: 'flex', justifyContent: 'center' }}>
          <h1 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontWeight: 700,
            color: '#bfc5e4',
            letterSpacing: '-0.01em',
            fontSize: 'clamp(32px, 5vw, 40px)',
          }}>
            BYOF
          </h1>
        </div>
      </header>

      {/* Main content */}
      <main style={{
        position: 'relative', zIndex: 10,
        width: '100%', maxWidth: '1280px',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', textAlign: 'center',
      }}>

        {/* Headline + subtitle */}
        <div style={{ maxWidth: '640px', marginBottom: '48px' }}>
          <h2 style={{
            fontFamily: "'Playfair Display', Georgia, serif",
            fontWeight: 700,
            color: '#e0e3e5',
            lineHeight: 1.2,
            textShadow: '0 2px 8px rgba(0,0,0,0.4)',
            fontSize: 'clamp(40px, 8vw, 64px)',
            letterSpacing: '-0.02em',
            marginBottom: '24px',
          }}>
            Your world, curated.
          </h2>
          <p style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '18px', fontWeight: 400,
            color: '#c6c6ce',
            lineHeight: 1.6,
            maxWidth: '480px',
            margin: '0 auto',
          }}>
            A daily feed of the content that matters to you, delivered in an immersive, focused experience.
          </p>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={onSignIn}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px',
              background: hovered ? 'rgba(191,197,228,0.20)' : 'rgba(191,197,228,0.10)',
              border: '1px solid rgba(191,197,228,0.20)',
              color: '#bfc5e4',
              padding: '16px 32px',
              borderRadius: '9999px',
              fontFamily: "'Hanken Grotesk', sans-serif",
              fontSize: '14px', fontWeight: 600,
              letterSpacing: '0.05em',
              minWidth: '280px',
              cursor: 'pointer',
              boxShadow: '0 0 15px rgba(105,212,244,0.10)',
              transition: 'background 200ms',
            }}
          >
            <span
              className="material-symbols-outlined icon-filled"
              style={{ fontSize: '20px', color: '#bfc5e4' }}
            >
              login
            </span>
            Sign in with Google
          </button>

          <p style={{
            fontFamily: "'Hanken Grotesk', sans-serif",
            fontSize: '14px',
            color: 'rgba(198,198,206,0.70)',
          }}>
            Join the curated experience.
          </p>
        </div>

      </main>
    </div>
  )
}
