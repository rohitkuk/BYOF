# BYOF Visual & Functional Test Plan
## Against Glacier Modern Editorial Design System + 5 Reference Screens

**Source of truth:** `design/screens/{feed,explore,saved,profile,landing}.html` + `docs/DESIGN.md`
**Test URL:** http://localhost:5173
**Device targets:** Mobile 390×844 (primary) + Desktop 1280px+

Pass criteria: exact match to reference screen. No approximations.

---

## LEGEND

- `[ ]` = not tested
- `[P]` = PASS — matches reference exactly
- `[F]` = FAIL — deviation found (note delta)
- `[S]` = SKIP — not yet implemented (marked Future)

---

## 0 · GLOBAL — Design System Tokens

These apply on every page. Test first.

### 0.1 Color Palette

| # | Check | Expected | Result |
|---|-------|----------|--------|
| G-01 | Page background | `#101415` on Feed/Explore/Saved/Profile — exception: Landing uses `#0a1128` | `[ ]` |
| G-02 | No undeclared colors | Only tokens from DESIGN.md: primary `#bfc5e4`, secondary `#93cfeb`, tertiary `#69d4f4`, surfaces, text, outlines | `[ ]` |
| G-03 | No coral, no orange, no bright white (#fff) on text | Inspect all colored elements | `[ ]` |
| G-04 | Glacier Blue (#93cfeb) on interactive/active elements | Like active, nav active, Apply buttons | `[ ]` |
| G-05 | Cerulean (#69d4f4) on save-active and Apply Filters CTA | Exact hex match | `[ ]` |
| G-06 | Midnight Lavender (#bfc5e4) on BYOF wordmark and primary text accents | Exact hex match | `[ ]` |

### 0.2 Typography

| # | Check | Expected | Result |
|---|-------|----------|--------|
| G-07 | Playfair Display loaded | Network tab shows font request succeeds | `[ ]` |
| G-08 | Hanken Grotesk loaded | Network tab shows font request succeeds | `[ ]` |
| G-09 | Material Symbols Outlined loaded | Icon font request succeeds; no □ placeholders | `[ ]` |
| G-10 | BYOF wordmark font | Playfair Display, bold, Midnight Lavender — on all pages | `[ ]` |
| G-11 | Body text font | Hanken Grotesk throughout — never Playfair on labels/meta/buttons | `[ ]` |
| G-12 | No system/fallback fonts visible | No Arial, Times, etc. rendered anywhere | `[ ]` |

### 0.3 Elevation & Depth

| # | Check | Expected | Result |
|---|-------|----------|--------|
| G-13 | No hard box-shadows | Only `backdrop-filter: blur()` and tonal layering | `[ ]` |
| G-14 | Frosted glass on nav bars | `backdrop-filter: blur(12px+)`, semi-transparent bg | `[ ]` |
| G-15 | Active glow effect | Cerulean `box-shadow: 0 0 15–20px rgba(105,212,244,0.2–0.3)` on active segments/CTAs | `[ ]` |

### 0.4 Radius

| # | Check | Expected | Result |
|---|-------|----------|--------|
| G-16 | Buttons are pill-shaped | `border-radius: 9999px` on all buttons | `[ ]` |
| G-17 | Cards use `--radius-lg` (2rem) | Main cards rounded-lg style | `[ ]` |
| G-18 | Inputs use `--radius` (1rem) | Search bar, segmented control container | `[ ]` |

---

## 1 · TOPBAR (shared component — all pages)

**Reference:** `feed.html` lines 113–121 (desktop), lines 184–191 (mobile) | `explore.html` lines 175–194

### 1.1 Mobile TopBar Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| T-01 | Height | 64px fixed | `[ ]` |
| T-02 | Background | `rgba(16,20,21,0.85)` with `backdrop-filter: blur(12px)` | `[ ]` |
| T-03 | Bottom border | `1px solid rgba(255,255,255,0.05)` | `[ ]` |
| T-04 | Layout | 3-item flex row: hamburger (left) · BYOF (center) · avatar (right) | `[ ]` |
| T-05 | Hamburger icon | `menu` Material Symbol, color `#bfc5e4` (primary), 24px | `[ ]` |
| T-06 | BYOF wordmark | Playfair Display, `font-weight: 700`, `#bfc5e4`, centered | `[ ]` |
| T-07 | Avatar button | 40×40px circle, `background: var(--surface-high)`, `border: 1px solid var(--outline-variant)` | `[ ]` |
| T-08 | Avatar icon | `person` Material Symbol, 20px, `var(--text-muted)` | `[ ]` |
| T-09 | TopBar is sticky/fixed | Does not scroll with content | `[ ]` |
| T-10 | TopBar z-index above feed cards | Feed cards scroll behind it | `[ ]` |

### 1.2 Desktop TopBar Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| T-11 | Height | 64px | `[ ]` |
| T-12 | Layout | Left: hamburger+BYOF · Center: nav links · Right: avatar | `[ ]` |
| T-13 | Nav links present | For You · Explore · Saved · Profile | `[ ]` |
| T-14 | Nav link font | Hanken Grotesk, 14px, weight 600, `letter-spacing: 0.05em` | `[ ]` |
| T-15 | Active nav link color | `#bfc5e4` (primary) + `border-bottom: 2px solid var(--primary)` | `[ ]` |
| T-16 | Inactive nav link color | `#909098` (text-dim) | `[ ]` |
| T-17 | Explore nav link has icon | `explore` Material Symbol (filled when active) inline with text | `[ ]` |
| T-18 | Max-width constraint | Content confined to 1280px, centered | `[ ]` |
| T-19 | Content padding | `0 24px` horizontal padding | `[ ]` |

### 1.3 TopBar Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| T-20 | Click BYOF wordmark → navigate to feed | View switches to feed (For You) | `[ ]` |
| T-21 | Click avatar → navigate to profile | Profile page renders | `[ ]` |
| T-22 | Desktop: click For You → feed | Feed view renders | `[ ]` |
| T-23 | Desktop: click Explore → explore | Explore page renders, Explore nav link becomes active | `[ ]` |
| T-24 | Desktop: click Saved → saved | Saved page renders | `[ ]` |
| T-25 | Desktop: click Profile → profile | Profile page renders | `[ ]` |
| T-26 | Active link updates on view change | When navigating via bottom nav, desktop active link also updates | `[ ]` |
| T-27 | Hamburger button — no-op in V1 | Tapping `menu` icon does nothing (no drawer, no crash, no console error) | `[ ]` |

---

## 2 · BOTTOM NAV (mobile only)

**Reference:** `feed.html` lines 192–212 · `explore.html` lines 291–308

### 2.1 Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| B-01 | Height | ~76px (py-3 pb-6 + content) | `[ ]` |
| B-02 | Position | Fixed bottom, full width, z-index 50 | `[ ]` |
| B-03 | Background | `rgba(29,32,34,0.92)` with `backdrop-filter: blur(20px)` | `[ ]` |
| B-04 | Top border | `1px solid rgba(255,255,255,0.08)` | `[ ]` |
| B-05 | Border radius (top) | `16px 16px 0 0` — rounded top corners | `[ ]` |
| B-06 | Hidden on desktop ≥768px | Bottom nav invisible at desktop breakpoint | `[ ]` |
| B-07 | 4 tabs | For You · Explore · Saved · Profile | `[ ]` |
| B-08 | Tab icons | `auto_awesome` · `explore` · `bookmark` · `person` (Material Symbols) | `[ ]` |
| B-09 | Icon size | 24px | `[ ]` |
| B-10 | Tab label font | Hanken Grotesk, 10px, weight 600, `letter-spacing: 0.05em` | `[ ]` |
| B-11 | Active tab style | `background: var(--secondary-container)` pill + `color: var(--on-secondary-container)` + icon filled | `[ ]` |
| B-12 | Active tab dot indicator | 4px circle below icon, `background: var(--secondary)` | `[ ]` |
| B-13 | Inactive tab color | `var(--text-dim)` (#909098) | `[ ]` |
| B-14 | Active icon filled | `icon-filled` class applied (FILL=1) on active tab | `[ ]` |

### 2.2 Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| B-15 | Tap For You → feed view | Feed renders, For You tab active | `[ ]` |
| B-16 | Tap Explore → explore view | Explore page renders, Explore tab active | `[ ]` |
| B-17 | Tap Saved → saved view | Saved page renders, Saved tab active | `[ ]` |
| B-18 | Tap Profile → profile view | Profile page renders, Profile tab active | `[ ]` |
| B-19 | Tab persists active state | Navigate away and back — correct tab stays active | `[ ]` |
| B-20 | Active tab updates when navigating via TopBar (desktop) | Cross-component state sync | `[ ]` |

---

## 3 · FEED PAGE (For You)

**Reference:** `design/screens/feed.html`
**Route:** Default view (view === 'feed')

### 3.1 Feed Card Visual — Image Layer

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-01 | Card height | 100vh (full viewport height) | `[ ]` |
| F-02 | Article image fills card | `position: absolute; inset: 0; object-fit: cover` | `[ ]` |
| F-03 | Gradient overlay | `linear-gradient(to top, rgba(10,17,40,0.97), rgba(10,17,40,0.55) 55%, transparent)` — bottom to top | `[ ]` |
| F-04 | Vignette overlay | Subtle `rgba(0,0,0,0.15)` over entire card | `[ ]` |
| F-05 | Fallback gradient when no image | `linear-gradient(135deg, #0b0f10, #1d2022, #272a2c)` | `[ ]` |
| F-06 | No broken image icon visible | `onError` hides img element, fallback shows | `[ ]` |

### 3.2 Feed Card Visual — Content Layer

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-07 | Category pill style | Border `rgba(147,207,235,0.5)`, bg `rgba(147,207,235,0.12)`, `backdropFilter: blur(8px)`, text `#93cfeb`, 11px Hanken Grotesk uppercase, `letter-spacing: 0.1em`, `border-radius: 9999px`, `padding: 4px 14px` | `[ ]` |
| F-08 | Read time displayed | `{n} MIN READ` in same area as category pill (dimmer style) | `[ ]` |
| F-09 | Title font | Playfair Display, 24px, weight 600, `color: var(--text-primary)`, `line-height: 1.3` | `[ ]` |
| F-10 | Title clamp | Max 3 lines, `WebkitLineClamp: 3` | `[ ]` |
| F-11 | Title text shadow | `text-shadow: 0 1px 4px rgba(0,0,0,0.5)` | `[ ]` |
| F-12 | Content area bottom offset | `calc(var(--bottom-nav-height) + 72px)` — clears bottom nav | `[ ]` |
| F-13 | Content area right margin | 80px — clears ActionRail on right | `[ ]` |

### 3.3 Feed Card Visual — Meta Bar

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-14 | Favicon | 24×24px circle, Google favicon API | `[ ]` |
| F-15 | Source name | Hanken Grotesk, 13px, weight 600, `var(--text-primary)` | `[ ]` |
| F-16 | Published date | `var(--text-dim)`, same size, formatted relative time | `[ ]` |
| F-17 | READ ↗ button | Hanken Grotesk 12px, weight 600, `var(--secondary)`, uppercase, no background, no border | `[ ]` |
| F-18 | Meta bar bottom offset | `calc(var(--bottom-nav-height) + 14px)` — above bottom nav | `[ ]` |
| F-19 | Meta bar right margin | 80px — clears ActionRail | `[ ]` |

### 3.4 Feed Card Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-20 | Click card → opens article | `window.open(url, '_blank', 'noopener,noreferrer')` | `[ ]` |
| F-21 | Click READ ↗ → opens article | Same URL, propagation stopped | `[ ]` |
| F-22 | Scroll snap | Snaps card-to-card, no partial cards visible mid-scroll | `[ ]` |
| F-23 | Scroll direction | Vertical only | `[ ]` |
| F-24 | Card visible behind TopBar | Image renders behind TopBar (TopBar is frosted glass overlay) | `[ ]` |
| F-25 | Card visible behind BottomNav | Image renders behind BottomNav on mobile | `[ ]` |
| F-26 | Content does NOT overlap BottomNav | Title, meta bar visible above bottom nav on mobile | `[ ]` |
| F-27 | Skipped card dims | When skip toggled: `rgba(0,0,0,0.45)` overlay appears on card | `[ ]` |
| F-28 | Skipped card undims on re-tap | Toggle skip again → overlay removed | `[ ]` |

### 3.5 Action Rail Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-29 | Rail position | Fixed right 16px, `bottom: calc(var(--bottom-nav-height) + 80px)` | `[ ]` |
| F-30 | Rail container | Frosted glass pill: `background: rgba(29,32,34,0.65)`, `backdropFilter: blur(20px)`, `border: 1px solid rgba(255,255,255,0.06)`, `border-radius: 9999px`, `padding: 8px` | `[ ]` |
| F-31 | 3 action buttons: Like, Save, Skip | Icons: `favorite`, `bookmark`, `close` (Material Symbols) | `[ ]` |
| F-32 | Button size | 48×48px circle | `[ ]` |
| F-33 | Button icon size | 24px | `[ ]` |
| F-34 | Inactive icon color | `var(--text-primary)` | `[ ]` |
| F-35 | Label font | Hanken Grotesk, 9px, uppercase, `var(--text-dim)` | `[ ]` |
| F-36 | Like active | `favorite` icon filled, color `var(--like-active)` = `#93cfeb` | `[ ]` |
| F-37 | Save active | `bookmark` icon filled, color `var(--save-active)` = `#69d4f4` | `[ ]` |
| F-38 | Skip active | `close` icon, color `var(--text-dim)` = `#909098` | `[ ]` |
| F-39 | Hover scale | `scale(1.1)` on hover | `[ ]` |
| F-40 | Button click stops card-click propagation | Tapping Like/Save/Skip does not navigate to article | `[ ]` |

### 3.6 Action Rail Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-41 | Like toggles | Tap Like: icon fills + turns Glacier Blue; tap again: unfills | `[ ]` |
| F-42 | Save toggles | Tap Save: icon fills + turns Cerulean; tap again: unfills | `[ ]` |
| F-43 | Skip toggles + dims card | Tap Skip: card dims; tap again: undims | `[ ]` |
| F-44 | Actions are per-item | Scrolling to next card resets rail state to that card's state | `[ ]` |
| F-45 | Saved signal persists to Saved page | Items saved via ActionRail appear in Saved Library | `[ ]` |

### 3.7 Progress Dots Visual (Desktop only)

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-46 | Hidden on mobile | `display: none` below 768px | `[ ]` |
| F-47 | Position | Fixed, right 32px, vertically centered (top 50% translateY -50%) | `[ ]` |
| F-48 | Active dot | 8×48px, `background: var(--secondary)` (#93cfeb), `border-radius: 9999px` | `[ ]` |
| F-49 | Inactive dot | 8×8px, `background: var(--surface-highest)` (#323537), `border-radius: 9999px` | `[ ]` |
| F-50 | Gap between dots | 12px | `[ ]` |
| F-51 | Active dot transitions | `height` animates smoothly on scroll | `[ ]` |
| F-52 | Updates on scroll | Active dot index matches visible card index | `[ ]` |

### 3.8 Feed Loading/Error States

| # | Check | Expected | Result |
|---|-------|----------|--------|
| F-53 | Loading spinner | Visible while `loading: true`; spinning circle `border-top: var(--secondary)` | `[ ]` |
| F-54 | Loading text | "Loading your feed…" Hanken Grotesk 16px `var(--text-muted)` | `[ ]` |
| F-55 | Error state icon | `wifi_off` Material Symbol 40px `var(--outline-variant)` | `[ ]` |
| F-56 | Error message | "Could not load feed." + "`api.py` running on :8000?" | `[ ]` |
| F-57 | Error message code style | `api.py` in tertiary (#69d4f4) monospace | `[ ]` |
| F-58 | Empty state icon | `inbox` Material Symbol | `[ ]` |
| F-59 | Empty state text | "No articles yet." + run `app.py` instruction | `[ ]` |

---

## 4 · EXPLORE PAGE

**Reference:** `design/screens/explore.html`
**Route:** view === 'explore'

### 4.1 Page Layout Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-01 | Page scrolls independently | Scrollable within `top: 64px; bottom: 76px` (mobile) | `[ ]` |
| E-02 | Background | `var(--bg)` = `#101415` | `[ ]` |
| E-03 | Max width | 1280px centered | `[ ]` |
| E-04 | Container padding | 24px horizontal | `[ ]` |

### 4.2 Mobile Header Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-05 | "Explore" heading | Playfair Display, 32px (mobile), weight 700, `letter-spacing: -0.02em`, `var(--text-primary)` | `[ ]` |
| E-06 | Subtitle | "Discover content that matters to you." Hanken Grotesk 16px `var(--text-muted)` `line-height: 1.6` | `[ ]` |
| E-07 | Mobile header padding | `padding-top: 32px; padding-bottom: 16px` | `[ ]` |

### 4.3 Desktop Header Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-08 | "Explore" heading | Playfair Display, 64px (desktop display-lg), weight 700, `letter-spacing: -0.02em` | `[ ]` |
| E-09 | Subtitle max-width | `max-width: 640px` | `[ ]` |
| E-10 | Desktop padding | `padding-top: 48px; padding-bottom: 32px` | `[ ]` |

### 4.4 Content Format Segmented Control Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-11 | Section label | "CONTENT FORMAT" Hanken Grotesk 11px, weight 600, `letter-spacing: 0.12em`, uppercase, `var(--text-dim)` | `[ ]` |
| E-12 | Control container | `background: var(--surface-low)` (#191c1e), `border: 1px solid rgba(255,255,255,0.05)`, `border-radius: 9999px`, `padding: 4px` | `[ ]` |
| E-13 | Options | All · Articles · Newsletters · Papers | `[ ]` |
| E-14 | Active segment | `background: var(--primary-container)` (#0a1128), `color: var(--on-primary-container)` (#767c99), `box-shadow: 0 0 15px rgba(105,212,244,0.25)` | `[ ]` |
| E-15 | Inactive segment | `background: none`, `color: var(--text-muted)` | `[ ]` |
| E-16 | Segment font | Hanken Grotesk 14px weight 600 `letter-spacing: 0.05em` | `[ ]` |
| E-17 | Horizontally scrollable on mobile | `overflow-x: auto`, no-scrollbar class | `[ ]` |
| E-18 | Spring animation on selection | `transition: all 300ms` smooth | `[ ]` |

### 4.5 Topics of Interest Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-19 | Section label | "TOPICS OF INTEREST" uppercase dim label style | `[ ]` |
| E-20 | Clear All button | Appears when topics selected, `color: var(--tertiary)` Hanken Grotesk 12px | `[ ]` |
| E-21 | Topic pills — inactive | `border: 1px solid var(--outline-variant)`, `color: var(--text-muted)`, `background: var(--surface-lowest)`, `border-radius: 9999px`, `padding: 8px 24px`, Hanken Grotesk 16px | `[ ]` |
| E-22 | Topic pills — active | `border: 2px solid var(--tertiary)`, `color: var(--tertiary)`, `background: rgba(105,212,244,0.10)` | `[ ]` |
| E-23 | Spring animation | `transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275)` | `[ ]` |
| E-24 | Pills wrap | `flex-wrap: wrap; gap: 12px` | `[ ]` |
| E-25 | 8 topic pills present | AI, Machine Learning, Technology, Research Papers, Science, Deep Learning, Programming, Minimalism | `[ ]` |

### 4.6 Preferred Sources Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-26 | Panel background | `var(--surface-lowest)` (#0b0f10), `border-radius: var(--radius)` (16px), `border: 1px solid rgba(255,255,255,0.08)`, `padding: 24px` | `[ ]` |
| E-27 | Panel header | "PREFERRED SOURCES" dim label + search icon `var(--text-dim)` | `[ ]` |
| E-28 | Source items present | All current sources: Google News, TechCrunch, Papers with Code, The Rundown AI | `[ ]` |
| E-29 | Source avatar | 40×40px circle, color-coded background (blue/green/amber/purple), white initials, Hanken Grotesk 13px bold | `[ ]` |
| E-30 | Source name font | Hanken Grotesk 16px | `[ ]` |
| E-31 | Active source item | `background: var(--bg)`, `border: 1px solid rgba(70,70,77,0.3)` | `[ ]` |
| E-32 | Active source checkbox | 24px circle, `background: var(--tertiary)`, `border: 2px solid var(--tertiary)`, `check` icon `var(--bg)` filled | `[ ]` |
| E-33 | Inactive source checkbox | 24px circle, `border: 2px solid var(--outline-variant)`, no fill | `[ ]` |
| E-34 | Select All / Deselect All toggle | Button at bottom of panel, `color: var(--tertiary)` | `[ ]` |

### 4.7 Desktop Grid Layout

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-35 | Left column: 8/12 cols | Content type + topics on left | `[ ]` |
| E-36 | Right column: 4/12 cols | Sources panel on right | `[ ]` |
| E-37 | Mobile: single column | Both sections stacked | `[ ]` |

### 4.8 CTA Area Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-38 | Reset button | `border: 1px solid var(--outline-variant)`, `color: var(--text-muted)`, `border-radius: 9999px`, `padding: 16px 32px` | `[ ]` |
| E-39 | Apply Filters button | `background: var(--tertiary)` (#69d4f4), `color: var(--on-tertiary)` (#003642), `border-radius: 9999px`, `padding: 16px 48px`, `box-shadow: 0 0 20px rgba(105,212,244,0.2)` | `[ ]` |
| E-40 | CTA row alignment | Right-aligned on desktop, wrapped on mobile | `[ ]` |

### 4.9 Explore Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| E-41 | Content type: tap All → clears type filter | `selectedType = null` | `[ ]` |
| E-42 | Content type: tap Articles → selects | `selectedType = 'Articles'` — segment glows | `[ ]` |
| E-43 | Content type: tap same again → deselects (returns to All) | `selectedType` toggles to `null` — same tap twice = clear | `[ ]` |
| E-44 | Content type: tap different → switches | Only one active at a time | `[ ]` |
| E-45 | Topics: tap pill → activates (tertiary glow) | `selectedTopics` includes topic | `[ ]` |
| E-46 | Topics: tap active pill → deactivates | Removed from array | `[ ]` |
| E-47 | Topics: multiple can be active | Multi-select allowed | `[ ]` |
| E-48 | Topics: Clear All → deactivates all | `setSelectedTopics([])` | `[ ]` |
| E-49 | Sources: tap inactive → activates with check | Toggle on | `[ ]` |
| E-50 | Sources: tap active → deactivates | Toggle off | `[ ]` |
| E-51 | Sources: Select All → all active | All sources checked | `[ ]` |
| E-52 | Sources: Select All again (Deselect All) → all clear | All unchecked | `[ ]` |
| E-53 | Apply Filters → navigates to Feed | `view = 'feed'`, filters applied | `[ ]` |
| E-54 | Apply Filters → feed refetches with type filter | API called with `?type=Article` etc. | `[ ]` |
| E-55 | Apply Filters → feed refetches with source filter | API called with `?source=TechCrunch` etc. | `[ ]` |
| E-56 | Reset → clears all, navigates to feed unfiltered | `setFilters({})`, feed shows all items | `[ ]` |
| E-57 | Returning to Explore → previous state cleared | Fresh state each visit | `[ ]` |

---

## 5 · SAVED PAGE

**Reference:** `design/screens/saved.html`
**Route:** view === 'saved'

### 5.1 Page Layout Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-01 | Page scrolls | Scrollable content between TopBar and BottomNav | `[ ]` |
| S-02 | Background | `var(--bg)` #101415 | `[ ]` |
| S-03 | Container padding | 24px horizontal | `[ ]` |

### 5.2 Header Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-04 | "BYOF" wordmark centered | Playfair Display 32px weight 700, `var(--text-primary)`, centered | `[ ]` |
| S-05 | "Saved Library" subtitle | Hanken Grotesk 11px uppercase `letter-spacing: 0.12em` `var(--text-dim)`, centered | `[ ]` |
| S-06 | Header top padding | 32px | `[ ]` |

### 5.3 Search Bar Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-07 | Search container | `max-width: 672px` | `[ ]` |
| S-08 | Search background | `var(--surface-highest)` (#323537) | `[ ]` |
| S-09 | Search border | `1px solid rgba(255,255,255,0.08)`, `border-radius: 9999px` | `[ ]` |
| S-10 | Search icon | `search` Material Symbol 20px `var(--outline)`, absolute left 16px | `[ ]` |
| S-11 | Search padding | `12px 16px 12px 48px` | `[ ]` |
| S-12 | Search placeholder | "Search your library…" `var(--text-muted)` | `[ ]` |
| S-13 | Search font | Hanken Grotesk 16px `var(--text-primary)` | `[ ]` |

### 5.4 Type Filter Pills Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-14 | Filter options | All · Article · Newsletter · Paper | `[ ]` |
| S-15 | Active pill | `background: var(--tertiary)`, `color: var(--on-tertiary)` (#003642), `border: none` | `[ ]` |
| S-16 | Inactive pill | `background: transparent`, `border: 2px solid var(--tertiary)`, `color: var(--tertiary)` | `[ ]` |
| S-17 | Pill border-radius | 9999px | `[ ]` |
| S-18 | Pills scrollable horizontally | `overflow-x: auto no-scrollbar -mx-4 px-4` pattern | `[ ]` |
| S-19 | "All" pill active by default | All active on page load | `[ ]` |

### 5.5 Saved Card Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-20 | Card background | `var(--surface-low)` (#191c1e) | `[ ]` |
| S-21 | Card border | `1px solid rgba(255,255,255,0.08)` | `[ ]` |
| S-22 | Card border-radius | 16px (`var(--radius)`) | `[ ]` |
| S-23 | Thumbnail size | 96×96px, `border-radius: 12px` | `[ ]` |
| S-24 | Thumbnail object-fit | `cover` | `[ ]` |
| S-25 | Type badge on thumbnail | `background: rgba(105,212,244,0.15)`, `color: var(--tertiary)`, `backdrop-filter: blur(8px)`, 10px uppercase Hanken Grotesk, top-left corner pill | `[ ]` |
| S-26 | Source name | Hanken Grotesk 12px `var(--text-dim)`, truncated | `[ ]` |
| S-27 | Dot separator | 4×4px `var(--outline-variant)` circle between source and time | `[ ]` |
| S-28 | Time | Hanken Grotesk 12px `var(--text-dim)` | `[ ]` |
| S-29 | Article title | Playfair Display 18px weight 500 `var(--text-primary)`, `line-height: 1.3`, max 2 lines | `[ ]` |
| S-30 | More options icon | `more_vert` Material Symbol 20px `var(--text-dim)` right side | `[ ]` |
| S-31 | Card gap | 16px between cards | `[ ]` |

### 5.6 Empty State Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-32 | Empty bookmark icon | `bookmark` Material Symbol 48px `var(--outline-variant)` centered | `[ ]` |
| S-33 | Empty heading | Playfair Display 20px `var(--text-muted)` "Nothing saved yet" | `[ ]` |
| S-34 | Empty instruction | Hanken Grotesk 14px `var(--text-dim)` "Tap the bookmark icon on any article to save it here." | `[ ]` |
| S-35 | Empty padding | 80px top/bottom | `[ ]` |

### 5.7 Saved Page Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| S-36 | Shows only saved items | Only items where `signals[url].saved === true` | `[ ]` |
| S-37 | Empty state when nothing saved | Shows empty state (not a blank page) | `[ ]` |
| S-38 | Filter All → shows all saved | No type filtering | `[ ]` |
| S-39 | Filter Article → shows only Articles | `item.type === 'Article'` | `[ ]` |
| S-40 | Filter Newsletter → shows only Newsletters | `item.type === 'Newsletter'` | `[ ]` |
| S-41 | Filter Paper → shows only Papers | `item.type === 'Paper'` | `[ ]` |
| S-42 | Search filters by title | Typing "AI" shows only matching items | `[ ]` |
| S-43 | Search + type filter combine | Both filters apply simultaneously | `[ ]` |
| S-44 | Click card → opens article in new tab | `window.open(url, '_blank')` | `[ ]` |
| S-45 | "No matches" state | When search/filter yields 0 results from non-empty saved list | `[ ]` |
| S-46 | Real-time search | Results update as user types, no submit needed | `[ ]` |

---

## 6 · PROFILE PAGE

**Reference:** `design/screens/profile.html`
**Route:** view === 'profile'

### 6.1 Page Layout Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-01 | Page scrolls | Scrollable between TopBar and BottomNav | `[ ]` |
| P-02 | Background | `var(--bg)` #101415 | `[ ]` |
| P-03 | Max width | 1280px centered | `[ ]` |
| P-04 | Gap between sections | 32px | `[ ]` |

### 6.2 Avatar Section Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-05 | Avatar circle | 96×96px, `background: var(--surface-high)`, `border: 2px solid rgba(191,197,228,0.2)` | `[ ]` |
| P-06 | Avatar glow | `box-shadow: 0 0 20px rgba(105,212,244,0.15)` — cerulean soft glow | `[ ]` |
| P-07 | Avatar icon | `person` Material Symbol 48px `var(--primary)` | `[ ]` |
| P-08 | Edit button | 28×28px circle, `background: var(--primary-container)`, `border: 1px solid rgba(255,255,255,0.1)`, `edit` icon 14px `var(--primary)`, absolute bottom-right of avatar | `[ ]` |
| P-09 | Display name | Playfair Display 24px weight 500 `var(--text-primary)` | `[ ]` |
| P-10 | Subtitle | Hanken Grotesk 14px `var(--text-dim)` — "Local-first · Private by design" | `[ ]` |
| P-11 | Avatar section centered | `flex-direction: column; align-items: center` | `[ ]` |

### 6.3 Stats Row Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-12 | Stats container | `background: var(--surface-low)`, `border-radius: var(--radius)`, `border: 1px solid rgba(255,255,255,0.06)`, `padding: 24px` | `[ ]` |
| P-13 | 3 stat items | Articles Read · Saved · Liked | `[ ]` |
| P-14 | Stat icon | Material Symbol 24px `var(--text-dim)` | `[ ]` |
| P-15 | Stat value | Playfair Display 22px weight 600 `var(--text-primary)` | `[ ]` |
| P-16 | Stat label | Hanken Grotesk 11px uppercase `letter-spacing: 0.08em` `var(--text-dim)` | `[ ]` |
| P-17 | Equal flex distribution | 3 stats spread evenly | `[ ]` |

### 6.4 Preferences Section Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-18 | Panel background | `var(--surface-lowest)`, `border-radius: var(--radius)`, `border: 1px solid rgba(255,255,255,0.06)`, `padding: 24px` | `[ ]` |
| P-19 | Section label | "READING PREFERENCES" dim uppercase label | `[ ]` |
| P-20 | Tune icon | `tune` Material Symbol 18px `var(--text-dim)` right | `[ ]` |
| P-21 | Preference pills | `border: 1px solid var(--outline-variant)`, `color: var(--text-muted)`, `border-radius: 9999px`, `padding: 6px 16px`, Hanken Grotesk 13px | `[ ]` |
| P-22 | Empty state text | If no preferences: message with `preferences.json` in tertiary monospace | `[ ]` |

### 6.5 App Info Section Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-23 | Panel background | `var(--surface-low)` | `[ ]` |
| P-24 | 3 info rows | Local-first · Private · Open sources | `[ ]` |
| P-25 | Row icon circle | 40×40px `var(--surface-high)`, `secondary` colored icon 20px | `[ ]` |
| P-26 | Row label | Hanken Grotesk 14px weight 600 `var(--text-primary)` | `[ ]` |
| P-27 | Row description | Hanken Grotesk 13px `var(--text-dim)` | `[ ]` |

### 6.6 Profile Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| P-28 | Preferences load from API | GET /preferences called; categories/subcategories shown as pills | `[ ]` |
| P-29 | Loading state | "Loading…" text while fetching | `[ ]` |
| P-30 | Edit button present | Visible on avatar — non-functional in V1 | `[ ]` |
| P-31 | Saved count reflects signals | "Saved" stat = count of items where `signals[url].saved === true` | `[ ]` |
| P-32 | Liked count reflects signals | "Liked" stat = count of items where `signals[url].liked === true` | `[ ]` |

---

## 7 · LANDING / LOGIN PAGE

**Reference:** `design/screens/landing.html`
**Route:** Shown when `localStorage.getItem('byof_signed_in')` is absent (first visit / cleared storage)

### 7.1 Visual

| # | Check | Expected | Result |
|---|-------|----------|--------|
| L-01 | Page background | `#0a1128` — midnight navy, distinct from feed's `#101415` | `[ ]` |
| L-02 | Ambient image opacity | Background image rendered at `opacity: 0.30`, `mix-blend-mode: overlay` | `[ ]` |
| L-03 | Gradient overlay | `linear-gradient(to top, #0a1128, rgba(10,17,40,0.80) 50%, transparent)` — darkens bottom | `[ ]` |
| L-04 | No TopBar | Header bar (TopBar component) is NOT rendered | `[ ]` |
| L-05 | No BottomNav | Bottom navigation is NOT rendered | `[ ]` |
| L-06 | BYOF wordmark | Playfair Display, weight 700, `#bfc5e4`, centered in absolute header, `clamp(32px, 5vw, 40px)` | `[ ]` |
| L-07 | Wordmark position | `position: absolute; top: 0`, `padding: 24px`, centered via flexbox | `[ ]` |
| L-08 | Heading "Your world, curated." | Playfair Display, weight 700, `#e0e3e5`, `clamp(40px, 8vw, 64px)`, `letter-spacing: -0.02em`, `text-shadow: 0 2px 8px rgba(0,0,0,0.4)` | `[ ]` |
| L-09 | Subtitle text | "A daily feed of the content that matters to you, delivered in an immersive, focused experience." Hanken Grotesk 18px `#c6c6ce` `line-height: 1.6` | `[ ]` |
| L-10 | Subtitle max-width | `max-width: 480px` centered | `[ ]` |
| L-11 | Sign in button shape | Pill `border-radius: 9999px`, `min-width: 280px`, `padding: 16px 32px` | `[ ]` |
| L-12 | Sign in button background | `rgba(191,197,228,0.10)` at rest | `[ ]` |
| L-13 | Sign in button border | `1px solid rgba(191,197,228,0.20)` | `[ ]` |
| L-14 | Sign in button color | `#bfc5e4` text | `[ ]` |
| L-15 | Sign in button glow | `box-shadow: 0 0 15px rgba(105,212,244,0.10)` | `[ ]` |
| L-16 | Sign in button icon | `login` Material Symbol 20px FILL=1, left of text, `gap: 12px` | `[ ]` |
| L-17 | Sign in button font | Hanken Grotesk 14px weight 600 `letter-spacing: 0.05em` | `[ ]` |
| L-18 | Sub-text below button | "Join the curated experience." Hanken Grotesk 14px `rgba(198,198,206,0.70)` | `[ ]` |
| L-19 | Full viewport, no scroll | `height: 100vh; overflow: hidden` | `[ ]` |
| L-20 | Content centered | Main content flexbox column, centered vertically and horizontally | `[ ]` |

### 7.2 Functional

| # | Check | Expected | Result |
|---|-------|----------|--------|
| L-21 | First visit (no localStorage) → landing shown | Clear `byof_signed_in` key, reload → landing page renders | `[ ]` |
| L-22 | Click "Sign in with Google" → navigates to feed | No spinner, no OAuth — instantly shows Feed page | `[ ]` |
| L-23 | localStorage key set after sign-in | DevTools → Application → Local Storage → `byof_signed_in = '1'` | `[ ]` |
| L-24 | Reload after sign-in → feed loads directly | Landing page not shown again | `[ ]` |
| L-25 | Clear storage + reload → landing reappears | Auth gate resets correctly | `[ ]` |
| L-26 | Hover on button → background lightens | `rgba(191,197,228,0.20)` on hover, `transition: background 200ms` | `[ ]` |
| L-27 | No console errors on landing | Zero errors in DevTools console | `[ ]` |

---

## 8 · CROSS-PAGE / NAVIGATION

| # | Check | Expected | Result |
|---|-------|----------|--------|
| N-01 | Feed view: TopBar + BottomNav render on top | z-index 50 above feed (z:0) | `[ ]` |
| N-02 | Explore view: TopBar + BottomNav render correctly | Explore within `top:64px; bottom:76px` | `[ ]` |
| N-03 | Saved view: TopBar + BottomNav render correctly | Same layout as Explore | `[ ]` |
| N-04 | Profile view: TopBar + BottomNav render correctly | Same layout | `[ ]` |
| N-05 | Navigate Explore → Feed → state preserved | Feed scroll position and signals unchanged | `[ ]` |
| N-06 | Navigate Feed → Saved → back to Feed | Saved items from ActionRail appear in Saved | `[ ]` |
| N-07 | Body no unwanted scroll | `body { overflow: hidden }` prevents page-level scroll on all views | `[ ]` |
| N-08 | No page flash on navigation | Instant view switch, no white flash | `[ ]` |
| N-09 | Landing → Feed transition | No flash; feed loads immediately on sign-in | `[ ]` |
| N-10 | Landing: no TopBar/BottomNav bleeds in | App shell completely absent on landing | `[ ]` |

---

## 9 · RESPONSIVE / BREAKPOINTS

| # | Check | Expected | Result |
|---|-------|----------|--------|
| R-01 | Mobile 390px: BottomNav visible, no desktop nav | `mobile-only` shows, `desktop-only` hidden | `[ ]` |
| R-02 | Desktop 1280px: top nav links visible, no BottomNav | `desktop-only` shows, `mobile-only` hidden | `[ ]` |
| R-03 | ProgressDots: desktop only | Hidden on mobile, visible on desktop | `[ ]` |
| R-04 | ActionRail: visible on both | No responsive hiding | `[ ]` |
| R-05 | Explore page: 2-col grid on desktop, 1-col on mobile | `.explore-left` grid-column 1/9 on desktop | `[ ]` |
| R-06 | Feed card: 100vh on both | No size change at breakpoint | `[ ]` |
| R-07 | Tablet 768px: edge case | Correct breakpoint, no layout bleed | `[ ]` |
| R-08 | Landing: mobile wordmark size | `clamp(32px, 5vw, 40px)` — resolves to ~32px on 390px screen | `[ ]` |
| R-09 | Landing: sign-in button width | Mobile: full width (100%); desktop: `min-width: 280px` auto-sized | `[ ]` |

---

## 10 · PERFORMANCE & EDGE CASES

| # | Check | Expected | Result |
|---|-------|----------|--------|
| X-01 | API offline → error state (not crash) | Feed shows error UI, other pages still navigate | `[ ]` |
| X-02 | 0 feed items → empty state (not blank) | Empty state renders | `[ ]` |
| X-03 | Item with no image → gradient fallback | No broken img | `[ ]` |
| X-04 | Item with no categories → no pills | Pill row empty, no layout break | `[ ]` |
| X-05 | Very long title → clamps at 3 lines | WebkitLineClamp works | `[ ]` |
| X-06 | Very long source name → truncates | `text-overflow: ellipsis` | `[ ]` |
| X-07 | 20 items: ProgressDots count | Dots capped at 30 max | `[ ]` |
| X-08 | No saved items → Saved shows empty state | Not a blank div | `[ ]` |
| X-09 | Save item → go to Saved → item appears | Signal propagates to SavedPage | `[ ]` |
| X-10 | Console errors | Zero console errors on all pages | `[ ]` |
| X-11 | No undeclared colors in DevTools | Computed color inspector shows only Glacier hex values | `[ ]` |
| X-12 | Font rendering | All fonts anti-aliased, no fallback fonts rendered | `[ ]` |
| X-13 | Landing ambient image fails to load | No broken-image icon (alt=""), background color `#0a1128` still renders, gradient still shows | `[ ]` |
| X-14 | Rapid sign-in clicks | Click "Sign in with Google" multiple times — localStorage set once, no double-render or crash | `[ ]` |

---

## HOW TO RUN

1. **Before starting:** DevTools → Application → Local Storage → delete `byof_signed_in` (ensures landing page shows)
2. Open http://localhost:5173 in Chrome, set device to iPhone 12 Pro (390×844) in DevTools
3. Run section 7 (Landing) first while unauthenticated; click sign-in to enter the app
4. Run sections 0–6, 8–10 in the app shell
5. For `[F]` items: note exact delta (e.g. "color is #888 not #909098" or "padding 12px not 16px")
6. Switch to desktop 1280px for responsive tests (sections 1.2, 3.7, 4.7, 9)
7. Open DevTools Computed tab to verify exact CSS values for color/font/spacing checks

## FAIL RESOLUTION PRIORITY

1. **Color violations** (wrong hex) — fix immediately, hard rule
2. **Font violations** (wrong typeface) — fix immediately, hard rule
3. **Missing components** (icon not showing, section absent)
4. **Sizing deviations** >4px
5. **Spacing deviations** >4px
6. **Functional failures** (actions don't work)
7. **Edge cases** (empty/error states)
