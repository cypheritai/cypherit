# 🔐 CypherIt

### Get the steps in 60sec or Less.

**TikTok speed. YouTube depth.**

Paste any YouTube tutorial → Get structured steps with video clips → Fix your problem.

🌐 **Live at [cypherit.ai](https://www.cypherit.ai)**

---

## 🎬 Demo

<p align="center">
  <a href="https://www.cypherit.ai">
    <img src="https://www.cypherit.ai/logo.png" alt="CypherIt" width="300">
  </a>
</p>

<p align="center">
  <strong>👆 Click to try it live!</strong>
</p>

> **Try it now:** [cypherit.ai](https://www.cypherit.ai) — Paste any YouTube tutorial URL!

**Example input:** `https://www.youtube.com/watch?v=0HBA9Nov17Q`

**What you get:**
- 📋 Step-by-step instructions
- 🛠️ Tools needed: USB drive, Mac, Admin password
- ⏱️ Time estimate: 30-45 minutes
- ⚠️ Warnings: "USB will be erased"
- 💡 Pro tips from the video

---

## ✨ What It Does

CypherIt extracts the essential steps from any YouTube tutorial. No 20-minute intros. No fluff. Just the fix.

**Features:**
- 🎯 **Step-by-step extraction** — AI-powered breakdown of any tutorial
- 📹 **Video clips** — Each step links to the exact timestamp
- 🛠️ **Quick Info** — Tools needed, time estimate, warnings, pro tips
- 🔗 **Shareable links** — Deep link directly to any step
- 📱 **Mobile-first** — Designed for fixing things on the go

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Anthropic API key](https://console.anthropic.com/)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the API
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
python -m http.server 3000
```

Open http://localhost:3000 and paste any YouTube URL!

---

## 🏗️ Architecture

```
cypherit/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
├── frontend/
│   └── index.html        # Single-page app
├── scripts/
│   └── health_check.sh   # Deployment verification
├── ROADMAP.md            # What we're building
├── CONTRIBUTING.md       # How to help
└── CHANGELOG.md          # What's shipped
```

**Tech Stack:**
- **Backend:** Python, FastAPI, Claude (Anthropic)
- **Frontend:** Vanilla HTML/CSS/JS
- **Transcripts:** youtube-transcript-api + ScraperAPI fallback
- **Hosting:** Railway

---

## 🤝 Contributing

We'd love your help! Check out [CONTRIBUTING.md](./CONTRIBUTING.md) to get started.

**Good first issues:**
- Improve extraction prompts
- Add support for Gemini/Groq/Ollama
- Frontend polish and animations
- Accessibility improvements
- Documentation and translations

---

## 🗺️ Roadmap

See [ROADMAP.md](./ROADMAP.md) for what's shipped and what's coming.

**Building now:**
- Popular Fixes gallery (curated categories)
- Community upvotes
- Multi-LLM support

---

## 📜 License

MIT License — see [LICENSE](./LICENSE)

---

## 🌬️ Team

Built by humans + AI, shipping fast.

- **Carlos** — Vision, Product, Strategy
- **Zephyr** — Code, AI, Architecture

---

**🌐 Website:** [cypherit.ai](https://www.cypherit.ai)  
**📧 Contact:** contact@cypherit.ai  
**🐙 GitHub:** [github.com/cypheritai/cypherit](https://github.com/cypheritai/cypherit)

---

*Ship fast. Help millions. 🔧*
