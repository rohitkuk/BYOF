"""
Demo recorder for BYOF.
Playwright records browser as webm; imageio-ffmpeg converts to GIF.
Injects click-ripple + scroll-arrow overlays into the page for visual polish.

Usage: uv run python scripts/record_demo.py
Output: docs/demo.gif
"""

import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import imageio_ffmpeg

VIEWPORT   = {"width": 390, "height": 844}
BASE_URL   = "http://localhost:5173"
VIDEO_DIR  = Path("docs/demo_raw")
OUTPUT_GIF = Path("docs/demo.gif")
FFMPEG     = imageio_ffmpeg.get_ffmpeg_exe()

# Injected before every page — click ripple + scroll arrow helpers
INIT_SCRIPT = """
(() => {
  /* ── Click ripple ── */
  document.addEventListener('click', (e) => {
    const s = 48;
    const el = document.createElement('div');
    el.style.cssText = [
      'position:fixed',
      `left:${e.clientX - s/2}px`,
      `top:${e.clientY - s/2}px`,
      `width:${s}px`,
      `height:${s}px`,
      'border-radius:50%',
      'background:rgba(255,255,255,0.20)',
      'border:2.5px solid rgba(255,255,255,0.90)',
      'pointer-events:none',
      'z-index:2147483647',
      'transform:scale(0)',
      'opacity:1',
      'transition:transform 200ms cubic-bezier(0.2,0,0,1),opacity 250ms ease 150ms',
    ].join(';');
    document.body.appendChild(el);
    requestAnimationFrame(() => { el.style.transform = 'scale(1)'; });
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 260);
    }, 200);
  }, true);

  /* ── Scroll arrow ── */
  window.__scrollArrow = () => {
    const el = document.createElement('div');
    el.textContent = '↓';
    el.style.cssText = [
      'position:fixed',
      'bottom:120px',
      'left:50%',
      'transform:translateX(-50%) scale(0.6)',
      'font-size:22px',
      'color:rgba(255,255,255,0.95)',
      'background:rgba(0,0,0,0.45)',
      'border-radius:50%',
      'width:38px','height:38px',
      'display:flex','align-items:center','justify-content:center',
      'pointer-events:none',
      'z-index:2147483647',
      'opacity:0',
      'transition:opacity 120ms, transform 150ms cubic-bezier(0.2,0,0,1)',
    ].join(';');
    document.body.appendChild(el);
    requestAnimationFrame(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateX(-50%) scale(1)';
    });
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(-50%) scale(0.6)';
      setTimeout(() => el.remove(), 200);
    }, 550);
  };
})();
"""

# Smooth-scroll feed container, disable snap during animation, show arrow
SCROLL_JS = """
(() => {
  const feed = document.querySelector('div[style*="scroll-snap-type"]')
            || [...document.querySelectorAll('*')].find(
                 el => el.scrollHeight > el.clientHeight &&
                       getComputedStyle(el).overflowY === 'scroll'
               );
  if (!feed) return;
  if (window.__scrollArrow) window.__scrollArrow();
  feed.style.scrollSnapType = 'none';
  feed.scrollTo({top: feed.scrollTop + feed.clientHeight, behavior: 'smooth'});
  setTimeout(() => { feed.style.scrollSnapType = 'y mandatory'; }, 800);
})();
"""


def w(seconds):
    time.sleep(seconds)


def scroll(page, after=0.85):
    page.evaluate(SCROLL_JS)
    w(after)


def run_demo():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=1,
            is_mobile=True,
            record_video_dir=str(VIDEO_DIR),
            record_video_size=VIEWPORT,
        )
        # Inject overlays into every page before any script runs
        ctx.add_init_script(INIT_SCRIPT)
        page = ctx.new_page()

        # ── Landing ──────────────────────────────────────────────────────
        print("Landing...")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        w(1.5)

        # ── Sign in ───────────────────────────────────────────────────────
        print("Sign in...")
        page.click("text=Sign in with Google")
        page.wait_for_load_state("networkidle")
        w(1.8)

        # ── Browse feed ───────────────────────────────────────────────────
        print("Browse feed...")
        w(0.8)                        # card 1
        scroll(page, after=0.85)      # → card 2
        scroll(page, after=0.85)      # → card 3  ← like
        page.click('[aria-label="Like"]');  w(0.35)
        scroll(page, after=0.85)      # → card 4  ← save
        page.click('[aria-label="Save"]');  w(0.35)
        scroll(page, after=0.85)      # → card 5  ← skip
        page.click('[aria-label="Skip"]');  w(0.35)

        # ── Explore ───────────────────────────────────────────────────────
        print("Explore...")
        page.click('[aria-label="Explore"]')
        page.wait_for_load_state("networkidle")
        w(1.4)
        try:
            pills = page.locator('button.spring')
            cnt = pills.count()
            if cnt > 0: pills.nth(0).click(); w(0.45)
            if cnt > 1: pills.nth(1).click(); w(0.45)
            if cnt > 2: pills.nth(2).click(); w(0.45)
        except Exception:
            pass

        # ── Saved ─────────────────────────────────────────────────────────
        print("Saved...")
        page.click('[aria-label="Saved"]')
        page.wait_for_load_state("networkidle")
        w(1.6)

        # ── Profile ───────────────────────────────────────────────────────
        print("Profile...")
        page.click('[aria-label="Profile"]')
        page.wait_for_load_state("networkidle")
        w(1.6)

        ctx.close()
        browser.close()

    recordings = sorted(VIDEO_DIR.glob("*.webm"))
    if not recordings:
        print("ERROR: no .webm in", VIDEO_DIR)
        return None
    webm = recordings[-1]
    print(f"Recorded: {webm.name} ({webm.stat().st_size / 1e6:.1f} MB)")
    return webm


def to_gif(webm: Path):
    print(f"Converting → {OUTPUT_GIF} ...")
    OUTPUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG, "-y", "-i", str(webm),
        "-vf",
        "fps=20,scale=390:-1:flags=lanczos,"
        "split[s0][s1];[s0]palettegen=max_colors=192[p];[s1][p]paletteuse=dither=bayer",
        "-loop", "0",
        str(OUTPUT_GIF),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise RuntimeError("ffmpeg failed")
    size = OUTPUT_GIF.stat().st_size / 1e6
    print(f"Done: {OUTPUT_GIF} ({size:.1f} MB)")
    return size


if __name__ == "__main__":
    print("=== BYOF Demo Recorder ===")
    webm = run_demo()
    if webm:
        to_gif(webm)
        print("Clean up: rm -rf docs/demo_raw/")
