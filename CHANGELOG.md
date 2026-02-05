# CypherIt Changelog & Verified Features

**Last Updated:** 2026-02-04 @ 7:11 PM EST

---

## ✅ VERIFIED WORKING (Do Not Break!)

### Core Functionality
- [x] **YouTube URL extraction** — Supports youtube.com, youtu.be, shorts
- [x] **Transcript fetching** — Direct + ScraperAPI proxy fallback
- [x] **SSL fix** — Monkey-patch requests to disable verification (Railway container issue)
- [x] **Retry logic** — 3 attempts direct, 2 attempts proxy with backoff
- [x] **Claude extraction** — Extracts title, problem, steps with timestamps
- [x] **Demo videos** — Pre-validated examples load instantly

### Frontend
- [x] **Responsive design** — Works on mobile + desktop
- [x] **Error display** — Clear error messages to user
- [x] **Loading state** — Shows "Extracting..." during processing

### Video Embeds
- [x] **Lazy loading** — Videos load after 500ms+ delay
- [x] **YouTube IFrame API** — Programmatic control of players
- [x] **Sound button** — 🔇/🔊 tap-to-unmute (mobile browser policy)
- [x] **Segment looping** — Videos loop within step's timestamp range
- [x] **70vh step height** — Each step fills viewport, scroll-snap enabled
- [x] **onStateChange** — Loop activates only when player actually playing

---

### Thumbnail + Tap-to-Play ✅ (Verified Feb 4, 2026 @ 1:41 PM)
- [x] **Instant thumbnails** — YouTube thumbnails load in milliseconds
- [x] **Tap-to-play** — Video only loads when user taps
- [x] **Timestamp badge** — Shows clip start time on thumbnail
- [x] **Auto-mute previous** — Only one step plays at a time
- [x] **Sound button sync** — Shows 🔊/🔇 based on state
- [x] **Hidden captions** — Caption box only appears when video activated

**Result:** "Executes flawlessly and loads instantly" — Carlos ✅

### Phase A: Helpful Voting ✅ (Verified Feb 5, 2026 @ 10:45 AM)
- [x] **Vote buttons** — 👍/👎 at top and bottom of results
- [x] **Backend API** — `/votes` endpoint for tracking
- [x] **Vote persistence** — Stored in JSON per video_id
- [x] **Repeat vote prevention** — LocalStorage tracks voted videos
- [x] **Vote counts display** — Shows helpful/not helpful counts
- [x] **Mobile responsive** — Compact buttons on small screens

**API Verified:**
- GET `/votes/{video_id}` ✅
- POST `/votes` ✅

### Featured Fixes Gallery ✅ (Verified Feb 5, 2026 @ 10:22 AM)
- [x] **Category system** — 6 categories (Home, Tech, Phone, Auto, Gaming, Kitchen)
- [x] **Gallery grid** — Cards with thumbnails, upvotes, difficulty badges
- [x] **Category filtering** — Click tabs to filter fixes
- [x] **Click to load** — Tap any card to extract steps instantly
- [x] **Mobile responsive** — Optimized grid for small screens
- [x] **Verified videos only** — Only videos with working transcripts

**Result:** "Everything is working great, and the overall look is impressive!" — Carlos ✅

### Monetization Prep ✅ (Verified Feb 4, 2026 @ 7:11 PM)
- [x] **Free Beta badge** — Subtle cyan gradient pill next to tagline
- [x] **Pro coming soon footer** — "Free during beta · Pro coming soon"
- [x] **Non-intrusive design** — Plants the seed without being pushy

**Result:** "Great work everything seems to be working properly!" — Carlos ✅

### Quick Info Section ✅ (Verified Feb 4, 2026 @ 6:51 PM)
- [x] **Tools Needed** — 🛠️ Physical items, software, prerequisites
- [x] **Time Estimate** — ⏱️ Realistic completion time
- [x] **Warnings** — ⚠️ Data loss risks, admin requirements
- [x] **Pro Tips** — 💡 Helpful shortcuts from the video
- [x] **Auto-hide empty** — Only shows items with content
- [x] **Backend extraction** — Claude extracts from transcript context

**Result:** "Great work on adding those resources! They look great!" — Carlos ✅

### Tagline Consistency ✅ (Verified Feb 4, 2026 @ 6:56 PM)
- [x] **Page title** — "Get the Steps in 60sec or Less"
- [x] **Share text** — "Got the steps in 60sec on CypherIt!"
- [x] **Demo fix** — "iPhone Fix" → "USB Installer" (accurate label)

### Mobile UX Improvements ✅ (Verified Feb 4, 2026 @ 6:17 PM)
- [x] **Clear button** — ✕ button left of input to quickly clear URL
- [x] **Mobile layout** — "Get Steps" button below input (not cramped inline)
- [x] **Logo tap = Reset** — Tap CypherIt logo to clear all and start fresh
- [x] **Cancel extraction** — "✕ Cancel" button during loading to abort
- [x] **AbortController** — Properly cancels fetch request on stop

**Result:** "Stunning great work! Everything works!" — Carlos ✅

### Share Links ✅ (Verified Feb 4, 2026 @ 6:00 PM)
- [x] **Share CypherIt button** — Share the app via native share or copy link
- [x] **Share step links** — Each step has shareable deep link
- [x] **Deep link navigation** — Shared links open directly to the step
- [x] **URL includes video + step** — Links preserve extraction state

**Result:** "The shared links work and take you to the steps!" — Carlos ✅

### Logo Integration ✅ (Verified Feb 4, 2026 @ 6:00 PM)
- [x] **Header logo** — CypherIt branding image replaces text
- [x] **Favicon** — 32x32 icon for browser tab
- [x] **Apple touch icon** — 180x180 for iOS home screen

### Live Captions ✅ (Verified Feb 4, 2026 @ 11:00 AM)
- [x] **Caption extraction** — Backend extracts transcript text per step
- [x] **Synced to video time** — Captions pause when video buffers
- [x] **Hidden until play** — Clean UI, captions appear on activation

**Bug Fixed:** Pydantic model was filtering out `caption` field — added to Step model.

### Video Looping ✅ (Verified Feb 4, 2026 @ 9:32 AM)
- [x] **Segment looping** — Videos loop within step timestamp range
- [x] **Minimum segment duration** — 8 seconds minimum per step
- [x] **Scroll-triggered activation** — Active step plays, others pause
- [x] **Topmost step priority** — Observer picks topmost visible step
- [x] **Step 1 forced active** — Ensures first step activates on load
- [x] **onStateChange detection** — Loop starts when player ACTUALLY playing
- [x] **Fresh load works** — No more delayed activation on first load

**Bugs Fixed:**
- `videoPlayers` string key mismatch (was using number)
- Observer picking wrong step (now uses topmost)
- Steps too small (now 70vh height)
- Loop not starting on fresh load (now uses YT.PlayerState.PLAYING)

---

## 📝 KNOWN ISSUES

1. **Duplicate timestamps** — Claude sometimes assigns same timestamp to multiple steps
   - Mitigation: Prompt updated to require 5s spacing
   - Mitigation: Frontend enforces 8s minimum segment

2. **499 errors from YouTube** — Transient rate limiting
   - Mitigation: Retry logic with backoff
   - Mitigation: Friendlier error message

3. **Mobile autoplay** — Browsers block autoplay with sound
   - Mitigation: Start muted, tap-to-unmute button

---

## 🚀 DEPLOYMENT CHECKLIST

Before every deploy, run:
```bash
./scripts/health_check.sh
```

Must pass:
1. `/health` — Returns 200
2. `/demos` — Returns 3 demo videos
3. `/extract` — Returns valid JSON with title, steps, video_id
4. Timestamps extracted — Has `[M:SS]` format timestamps
5. Video ID present — Response includes video_id

---

## 📅 Version History

### v0.7.0 (2026-02-05) — Helpful Voting (Phase A)
- 👍/👎 voting buttons on results page
- Vote tracking per video with API
- LocalStorage prevents repeat votes
- Foundation for community feedback system

### v0.6.0 (2026-02-05) — Featured Fixes Gallery
- Gallery with 6 categories
- Verified videos only (transcript validation)
- Mobile-responsive grid with thumbnails
- Click-to-load any fix instantly

### v0.5.0 (2026-02-04) — Quick Info + Monetization Prep
- Quick Info section: tools, time, warnings, pro tips
- "Free Beta" badge with Pro coming soon footer
- Tagline consistency across all share text
- Demo label fix: "iPhone Fix" → "USB Installer"

### v0.4.0 (2026-02-04) — Mobile UX Polish
- Clear button (✕) for quick URL clearing
- Mobile: "Get Steps" button moves below input
- Logo tap = reset/start fresh
- Cancel button during extraction with AbortController
- Custom logo, favicon, apple-touch-icon branding
- Share links with deep link navigation to steps

### v0.3.0 (2026-02-04) — Video Looping
- Added video looping within step segments
- Fixed: string/number key mismatch in boundary check
- Added minimum 8s segment duration
- Sound button for mobile unmute
- Retry logic for transient YouTube failures

### v0.2.0 (2026-02-03) — Video Embeds
- YouTube IFrame API integration
- Lazy-loaded embeds with IntersectionObserver
- Autoplay muted, unmute when active
- SSL certificate fix (monkey-patch)

### v0.1.0 (2026-02-02) — Initial Release
- Core extraction working
- Demo videos
- Railway deployment
- ScraperAPI proxy support
