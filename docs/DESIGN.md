# BYOF Design System
## Glacier Modern Editorial

---

## Brand & Style

The brand personality is premium, serene, and sophisticated.
**Modern Editorial with a Soft-Minimalist twist** — structured high-contrast
layouts of luxury publishing combined with an organic, curvy tactile language.
Sharp typography paired with deeply rounded containers.
Emotional target: "effortless luxury" — cool, fluid, meticulously organised.

---

## Color Tokens

### Surfaces (dark navy base)
| Token | Hex | Use |
|---|---|---|
| `--bg` | `#101415` | Page background |
| `--surface-lowest` | `#0b0f10` | Sidebar background |
| `--surface-low` | `#191c1e` | Subtle cards |
| `--surface` | `#1d2022` | Default card bg |
| `--surface-high` | `#272a2c` | Elevated elements |
| `--surface-highest` | `#323537` | Highest elevation |

### Accents
| Token | Hex | Name | Use |
|---|---|---|---|
| `--primary` | `#bfc5e4` | Midnight Lavender | Wordmark, primary text accents |
| `--secondary` | `#93cfeb` | Glacier Blue | Interactive elements, pills active, FAB |
| `--tertiary` | `#69d4f4` | Cerulean | Save active state, secondary actions |

### Text
| Token | Hex | Use |
|---|---|---|
| `--text-primary` | `#e0e3e5` | Body text, titles |
| `--text-muted` | `#c6c6ce` | Secondary text |
| `--text-dim` | `#909098` | Meta, timestamps, labels |

### Borders
| Token | Hex | Use |
|---|---|---|
| `--outline` | `#909098` | Default borders |
| `--outline-variant` | `#46464d` | Subtle dividers, inactive dots |

### Action states
| Token | Hex | Use |
|---|---|---|
| `--like-active` | `#93cfeb` | Like button active (Glacier Blue) |
| `--save-active` | `#69d4f4` | Save button active (Cerulean) |
| `--skip-active` | `#46464d` | Skip button active (muted) |

### Hard rule
**Never introduce a color not listed above.** No coral, no orange, no custom colours.
If a new colour is needed, add it here first.

---

## Typography

### Font pairing
- **Headlines, card titles, BYOF wordmark:** Playfair Display (serif)
- **Everything else:** Hanken Grotesk (sans-serif)

### Font import (add to index.css and any HTML file)
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Hanken+Grotesk:wght@400;600&display=swap');
```

### Type scale
| Role | Font | Size | Weight | Line height |
|---|---|---|---|---|
| Display | Playfair Display | 64px | 700 | 1.1 |
| Headline LG | Playfair Display | 40px | 600 | 1.2 |
| Headline LG mobile | Playfair Display | 32px | 600 | 1.2 |
| Headline MD | Playfair Display | 24px | 500 | 1.3 |
| Body LG | Hanken Grotesk | 18px | 400 | 1.6 |
| Body MD | Hanken Grotesk | 16px | 400 | 1.6 |
| Label | Hanken Grotesk | 14px | 600 | 1.4 |
| Caption | Hanken Grotesk | 11–12px | 600 | 1.4 |

### Hard rule
**Playfair Display for headlines and wordmark only.**
**Hanken Grotesk for everything else — labels, pills, meta, buttons, body.**

---

## Spacing

| Token | Value | Use |
|---|---|---|
| `--unit` | 8px | Base grid unit |
| `--container-padding` | 24px | Outer padding |
| `--gutter` | 16px | Inner gutter |
| `--section-gap` | 80px | Between sections |

---

## Radius

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | 0.5rem (8px) | Small elements |
| `--radius` | 1rem (16px) | Default, inputs |
| `--radius-md` | 1.5rem (24px) | Medium cards |
| `--radius-lg` | 2rem (32px) | Cards, main containers |
| `--radius-xl` | 3rem (48px) | Large containers |
| `--radius-full` | 9999px | Pills, buttons, tags |

---

## Elevation & Depth

Depth via **tonal layering** and **soft luminescence** — no hard shadows.

- **Level 0 (base):** `#101415`
- **Level 1 (cards):** Lighter navy tint + 1px inner border at 10% white opacity
- **Level 2 (popovers/modals):** `backdrop-filter: blur(12px)` + semi-transparent navy fill ("frosted obsidian")
- **Active states:** Soft diffused Glacier Blue outer glow instead of shadow

---

## Components

### Buttons
Strictly pill-shaped (`border-radius: 9999px`).
- Primary: solid Glacier Blue fill (`#93cfeb`), dark navy text (`#003546`)
- Secondary/ghost: 2px Glacier Blue border, matching text, transparent bg

### Cards
- `border-radius: 2rem` (32px)
- Background: subtle lighter navy tint
- No external shadow
- Padding: min 24px

### Inputs
- `border-radius: 1rem` (16px)
- Dark recessed navy bg
- 1px border → illuminates to Glacier Blue on focus

### Pills / Tags / Chips
- Always pill-shaped (`border-radius: 9999px`)
- Active: `background: #93cfeb`, text `#003546`
- Inactive: transparent bg, `border: 1.5px solid #46464d`, text `#c6c6ce`
- Glass indicator variant: Cerulean bg at 15% opacity, solid Cerulean text

### Action buttons (Like/Skip/Save)
- 56px circle
- `background: rgba(255,255,255,0.10)`, `backdrop-filter: blur(16px)`
- `border: 1px solid rgba(255,255,255,0.08)`
- Hover: `background: rgba(255,255,255,0.16)`, `scale(1.08)`

### Segmented controls
- Outer container + active thumb: both pill-shaped
- Active thumb glides between options with fluid spring animation

### Lists
- Vertical padding: 16px per item
- Selection state: 12px radius, does not touch list edges

---

## CSS Variables (index.css — copy verbatim)

```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Hanken+Grotesk:wght@400;600&display=swap');

:root {
  /* Surfaces */
  --bg:                     #101415;
  --surface-lowest:         #0b0f10;
  --surface-low:            #191c1e;
  --surface:                #1d2022;
  --surface-high:           #272a2c;
  --surface-highest:        #323537;

  /* Accents */
  --primary:                #bfc5e4;
  --secondary:              #93cfeb;
  --tertiary:               #69d4f4;
  --on-secondary:           #003546;

  /* Text */
  --text-primary:           #e0e3e5;
  --text-muted:             #c6c6ce;
  --text-dim:               #909098;

  /* Borders */
  --outline:                #909098;
  --outline-variant:        #46464d;

  /* Action states */
  --like-active:            #93cfeb;
  --save-active:            #69d4f4;
  --skip-active:            #46464d;

  /* Radius */
  --radius-sm:              0.5rem;
  --radius:                 1rem;
  --radius-md:              1.5rem;
  --radius-lg:              2rem;
  --radius-xl:              3rem;
  --radius-full:            9999px;

  /* Spacing */
  --unit:                   8px;
  --container-padding:      24px;
  --gutter:                 16px;

  /* Components */
  --action-btn-bg:          rgba(255,255,255,0.10);
  --sidebar-bg:             #0b0f10;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background: var(--bg);
  color: var(--text-primary);
  font-family: 'Hanken Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
}

h1, h2, h3, h4, .headline, .wordmark {
  font-family: 'Playfair Display', Georgia, serif;
}
```

---

## Reference Screens

All in `design/screens/` — **read the full HTML file before writing any component.**
Do not invent values — extract directly from the HTML.

| Screen | File | Used in step |
|---|---|---|
| Feed card (main) | `design/screens/feed.html` | Step 4 |
| Explore + filters | `design/screens/explore.html` | Step 6 |
| Saved library | `design/screens/saved.html` | Future |
| Profile | `design/screens/profile.html` | Future |
| Landing | `design/screens/landing.html` | Future |

Screenshots in `design/screenshots/` for visual reference.

---

## Migration Steps — Streamlit → FastAPI + React

One step per Claude Code session. Commit after each.
Do not start next step until previous is committed and verified.

**Context**
- Python pipeline untouched: `connectors/`, `agents/`, `db/`, `app.py`
- Only replacing `streamlit_app.py`
- Node v25.4.0 already installed
- FastAPI: `localhost:8000` — React: `localhost:5173`
- Privacy boundary unchanged — both processes run locally

---

### Step 1 — FastAPI backend `[ ]`

```
Enter plan mode. Step 1 of frontend migration. Build only what is listed.

Install: uv add fastapi uvicorn

Create api.py in project root:

GET /health → { "status": "ok" }

GET /preferences
  Reads preferences.json
  Returns { "categories": [...], "subcategories": {...} }

POST /preferences
  Body: { "categories": [...], "subcategories": {...} }
  Writes preferences.json → { "status": "ok" }

GET /feed
  Optional query params: category, date, type, source
  Runs weighing agent + aggregation agent on current DB
  Filters by query params if provided
  Returns JSON array up to 20 items:
  {
    "title": str,
    "url": str,
    "source": str,
    "published_at": str,      # "Just now"/"2h ago"/"Yesterday"/"3 days ago"
    "image_url": str | null,
    "image_type": str | null,
    "categories": list[str],
    "score": float,
    "read_time": int          # max(1, len(title.split()) // 3)
  }

POST /refresh
  Runs all connectors fetch() + save_items() +
  refresh_article_images(use_playwright=False) + refresh_publisher_logos()
  Returns { "status": "ok", "new_items": int }

CORS: allow http://localhost:5173
Port: 8000
__main__: uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

Verify:
1. uv run python api.py
2. http://localhost:8000/health → {"status":"ok"}
3. http://localhost:8000/feed → JSON array
4. http://localhost:8000/preferences → object

Pass → update CLAUDE.md Current State, stage api.py only,
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: add FastAPI backend (api.py)`

---

### Step 2 — React scaffold `[ ]`

```
Enter plan mode. Step 2. api.py working. Do not touch it.

Run:
  npm create vite@latest frontend -- --template react
  cd frontend && npm install && npm install axios

Create frontend/src/ structure:
  App.jsx
  components/FeedCard.jsx       (stub)
  components/ActionRail.jsx     (stub)
  components/ProgressDots.jsx   (stub)
  components/Sidebar.jsx        (stub)
  components/FilterPills.jsx    (stub)
  hooks/useFeed.js              (stub)
  hooks/usePreferences.js       (stub)
  styles/index.css

index.css: copy the full CSS block verbatim from docs/DESIGN.md
  (the block under "CSS Variables — copy verbatim")
  including @import, :root, *, body, h1/h2/h3 rules. Nothing else yet.

App.jsx: renders "BYOF" using Playfair Display,
  centered on --bg background. No data fetching yet.

Add to .gitignore: frontend/node_modules

Verify:
1. cd frontend && npm run dev
2. http://localhost:5173 → "BYOF" in Playfair Display on dark bg
3. No console errors

Pass → update CLAUDE.md, stage frontend/ (no node_modules),
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: scaffold React Vite frontend`

---

### Step 3 — Data hooks `[ ]`

```
Enter plan mode. Step 3. Scaffold done. Data layer only — no UI.

useFeed.js:
  fetch GET http://localhost:8000/feed on mount
  accepts filters object, re-fetches when filters change
  returns { items, loading, error, refetch }

usePreferences.js:
  fetch GET http://localhost:8000/preferences on mount
  exposes updatePreferences(data) → POST /preferences
  returns { preferences, loading, updatePreferences }

App.jsx:
  loading → "Loading your feed..." Hanken Grotesk, --text-muted
  error → "Could not load feed. Is api.py running?" --secondary
  success → "{n} items loaded" Playfair Display, --text-primary

Verify:
1. uv run python api.py (terminal 1)
2. cd frontend && npm run dev (terminal 2)
3. http://localhost:5173 shows real item count
4. No console errors

Pass → update CLAUDE.md, stage hooks/ + App.jsx,
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: wire React data hooks to FastAPI`

---

### Step 4 — FeedCard component `[ ]`

```
Enter plan mode. Step 4. Data hooks working.

FIRST: read design/screens/feed.html in full.
Extract layout, gradients, spacing, font usage.
Use only tokens from docs/DESIGN.md CSS variables block.

Card section wrapper:
  height 100vh, scroll-snap-align start
  position relative, overflow hidden

Image layer:
  position absolute, width 100%, height 100%, object-fit cover
  fallback: linear-gradient(135deg, #0b0f10, #1d2022, #272a2c)

Gradient overlay:
  position absolute, bottom 0, left 0, right 0, height 70%
  linear-gradient(to top, rgba(11,15,16,0.96), rgba(11,15,16,0.5) 60%, transparent)

Content overlay (absolute, bottom 80px, left 24px, right 80px):
  Category pills:
    border 1px solid var(--secondary), color var(--secondary)
    background rgba(147,207,235,0.12)
    Hanken Grotesk 11px uppercase letter-spacing 0.08em
    border-radius var(--radius-full), padding 4px 12px
  Title:
    Playfair Display 24px weight 600, color var(--text-primary)
    line-height 1.3, -webkit-line-clamp 3, margin-top 10px
  Excerpt:
    Hanken Grotesk 14px, color var(--text-muted)
    -webkit-line-clamp 2, margin-top 6px
    hide if empty or identical to title

Meta bar (absolute, bottom 20px, left 24px, right 80px):
  flex, justify-content space-between, align-items center
  Left: favicon 24px circle
        + source Hanken Grotesk bold 13px var(--text-primary)
        + " · " + published_at var(--text-dim)
        + " · " + read_time + " min read" var(--text-dim)
  Favicon: https://www.google.com/s2/favicons?domain={domain}&sz=32
  Right: "READ ↗" var(--secondary), 12px Hanken Grotesk bold uppercase
         window.open(url, '_blank')

Top bar (fixed z-index 100):
  FAB: top 16px left 16px, 48px circle
       background var(--secondary), ☰ icon color var(--on-secondary)
       onClick toggles sidebar
  BYOF: top 20px right 16px
       Playfair Display 18px weight 700
       color var(--primary), letter-spacing 0.1em

Feed container App.jsx:
  height 100vh, overflow-y scroll, scroll-snap-type y mandatory
  map items → section each height 100vh scroll-snap-align start
  empty divs for ActionRail and ProgressDots (step 5)

Verify:
1. Cards render — Playfair Display titles, Grotesk meta
2. Glacier palette — no coral, no bright white
3. READ opens article in new tab
4. Scroll snaps card to card
5. No console errors

Pass → update CLAUDE.md, stage FeedCard.jsx + App.jsx + styles/,
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: build FeedCard component`

---

### Step 5 — ActionRail + ProgressDots `[ ]`

```
Enter plan mode. Step 5. FeedCard done.
Re-read design/screens/feed.html — focus on right-side action buttons.

ActionRail.jsx:
  position absolute, right 16px, bottom 100px
  vertical flex, gap 16px, align-items center

Each button:
  56px circle, background var(--action-btn-bg)
  backdrop-filter blur(16px)
  border 1px solid rgba(255,255,255,0.08)
  border-radius var(--radius-full)
  cursor pointer, transition transform 150ms background 150ms
  hover: rgba(255,255,255,0.16) scale(1.08)

Icons 22px, default var(--text-muted)
Labels: Hanken Grotesk 10px uppercase var(--text-dim), margin-top 4px

LIKE (♥): active → icon var(--like-active)
SKIP (✕): active → icon var(--skip-active), card gets rgba(0,0,0,0.45) overlay
SAVE (bookmark): active → icon var(--save-active)

State: useState per ActionRail — liked, skipped, saved

// TODO V2: persist to db/store.py user_signals table
// keys: item_url, signal_type (like/skip/save), timestamp
// weighing agent consumes in V2 swarm

ProgressDots.jsx:
  position absolute, left 12px, top 50%, translateY(-50%)
  vertical flex, gap 4px
  Props: total, current
  Active: 3px × 20px var(--primary), border-radius 2px
  Inactive: 3px × 5px var(--outline-variant), border-radius 2px

IntersectionObserver in App.jsx:
  observe each card section ref
  >50% visible → setActiveIndex(i)

Verify:
1. LIKE → Glacier Blue
2. SKIP → muted, card dims
3. SAVE → Cerulean
4. Dots update on scroll
5. No console errors

Pass → update CLAUDE.md, stage ActionRail.jsx + ProgressDots.jsx + App.jsx,
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: add ActionRail and ProgressDots`

---

### Step 6 — Sidebar + FilterPills `[ ]`

```
Enter plan mode. Step 6. All cards working.
FIRST: read design/screens/explore.html in full.
Glacier tokens only — no new colours.

FilterPills.jsx:
  Props: label, options, selected, onChange, multiSelect
  Label: Hanken Grotesk 11px uppercase var(--text-dim) letter-spacing 0.1em
  Pills: flex wrap gap 8px
  Active: bg var(--secondary) color var(--on-secondary) border none
  Inactive: transparent bg, border 1.5px solid var(--outline-variant), color var(--text-muted)
  border-radius var(--radius-full), padding 8px 16px, font-size 14px

Sidebar.jsx:
  fixed top 0 left 0, height 100vh, width min(85vw, 340px)
  background var(--sidebar-bg), z-index 200
  transform translateX(-100%) → translateX(0)
  transition 280ms cubic-bezier(0.4,0,0.2,1)
  overflow-y auto

  Backdrop: fixed inset-0 z-index 199, rgba(0,0,0,0.6) blur(4px), onClick onClose

  Contents (padding 24px):
  1. "BYOF" Playfair Display 22px var(--primary) +
     × close 32px circle var(--surface-high)
  2. YOUR INTERESTS label + interest pills
     border 1.5px solid var(--secondary), color var(--secondary), bg transparent
  3. Edit preferences — full width var(--surface-high), var(--text-primary), var(--radius-md)
  4. hr border-top 1px solid var(--outline-variant) margin 20px 0
  5. FilterPills CATEGORY — single select, ["All", ...categories]
  6. FilterPills DATE — single select, ["All time","Today","This week","This month"]
  7. FilterPills TYPE — multi, ["Article","Newsletter","Paper","Video"]
  8. FilterPills SOURCE — multi, unique sources from items
  9. Apply filters — sticky bottom 24px, full width
     bg var(--secondary), color var(--on-secondary) bold
     border-radius var(--radius-full), padding 16px
     onClick: refetch with filters, onClose

Verify:
1. Drawer slides in with Glacier colours
2. Backdrop closes drawer
3. Pills match Glacier active/inactive states
4. Apply refetches and closes
5. Playfair Display "BYOF", Grotesk everything else
6. No console errors

Pass → update CLAUDE.md, stage Sidebar.jsx + FilterPills.jsx + App.jsx,
show summary, STOP — wait for "commit this"
```
**Commit:** `feat: add Sidebar and FilterPills`

---

### Step 7 — Cleanup and cutover `[ ]`

```
Enter plan mode. Step 7 — final cutover. Do not change component files.

1. Verify full pipeline end to end:
   - uv run python api.py (terminal 1)
   - cd frontend && npm run dev (terminal 2)
   - http://localhost:5173 loads, cards render
   - Glacier palette throughout — Playfair headlines, Grotesk body
   - Sidebar opens/closes, filters apply, action rail toggles
   - No console or terminal errors

2. Only if step 1 passes: delete streamlit_app.py
3. uv remove streamlit

4. Update CLAUDE.md:
   Current Focus → "Active slice: V1 Slice 7 — TechCrunch connector"
   Development section:
     Backend:  uv run python api.py       → http://localhost:8000
     Frontend: cd frontend && npm run dev → http://localhost:5173

5. Update README.md:
   Stack table: replace Streamlit with React (Vite) + FastAPI
   Getting Started: two-terminal setup
   Note: "Run app.py first for image backfill"

6. Update docs/ARCHITECTURE.md:
   Replace Streamlit section with React SPA section
   Add FastAPI section (api.py, :8000, CORS localhost:5173)

7. Stage all, show full diff, STOP — wait for "commit this"
```
**Commit:** `feat: migrate frontend to FastAPI + React, remove Streamlit`

---

## Hard Rules for All UI Work

- Never use a colour not in the Glacier palette above
- Playfair Display for headlines and wordmark **only**
- Hanken Grotesk for **everything else**
- Always read `design/screens/` HTML before building a component
- No Tailwind in React — extract values manually into `index.css`
- No UI frameworks, no component libraries — axios only
- No hard shadows — tonal layering and backdrop-blur only
