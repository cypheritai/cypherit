# CypherIt Changelog & Verified Features

**Last Updated:** 2026-02-04

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

---

## 🔧 IN PROGRESS / NEEDS VERIFICATION

### Video Looping (Feb 4, 2026)
- [ ] **Segment looping** — Videos should loop within step timestamp range
- [ ] **Minimum segment duration** — 8 seconds minimum per step
- [ ] **Scroll-triggered activation** — Active step plays, others pause

**Bug Fixed (this commit):** `videoPlayers` uses string keys, boundary check was using number — player lookup failed silently.

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
