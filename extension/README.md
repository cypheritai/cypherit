# CypherIt Chrome Extension

**Skip the fluff. Get the fix.** 🔧

Extract step-by-step solutions from YouTube tutorials in 60 seconds.

## Features

- **Popup Mode**: Click the extension icon on any YouTube video to extract steps
- **Inline Button**: A "Get Steps" button appears directly on YouTube video pages
- **One-Click Extraction**: Instantly sends video to CypherIt and shows results
- **Seamless Integration**: Results open in a new tab with cached extraction

## Installation (Developer Mode)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select this `extension` folder
5. The CypherIt icon appears in your toolbar!

## Usage

### Method 1: Popup
1. Navigate to any YouTube video
2. Click the CypherIt extension icon
3. Click "Extract Steps"
4. View your steps in a new tab

### Method 2: Inline Button
1. Navigate to any YouTube video
2. Look for the **🔧 Get Steps** button below the video (next to Like/Share)
3. Click it to extract and view steps

## Files

```
extension/
├── manifest.json     # Extension configuration
├── popup.html        # Popup UI
├── popup.js          # Popup logic
├── content.js        # Injects button on YouTube
├── content.css       # Button styles
├── icons/            # Extension icons
└── README.md         # This file
```

## Publishing to Chrome Web Store

1. Create a ZIP of the extension folder
2. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
3. Pay one-time $5 developer fee
4. Upload ZIP and fill in listing details
5. Submit for review (usually 1-3 days)

## Permissions

- `activeTab`: Read current tab URL
- `storage`: Save user preferences (future)
- Host access to `youtube.com` and `cypherit.ai`

---

Made with 🔧 by CypherIt
