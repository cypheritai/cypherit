# 🔐 CypherIt

**Decipher any problem in 60 seconds.**

TikTok speed + YouTube depth = CypherIt

## What is this?

CypherIt extracts the essential fix from any YouTube tutorial or article. No fluff. No 20-minute intros. Just the solution.

Paste a URL → Get structured steps → Fix your problem.

## Features

- 🎯 **60-second fixes** - Only the steps that matter
- 🛠️ **Parts & tools list** - Know what you need before you start  
- ⚠️ **Warnings included** - Avoid common mistakes
- ⏱️ **Time estimates** - Know how long it'll take
- 🔍 **Works on any "how to fix" video**

## Setup (Development)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# Run the API
python main.py
```

API runs at http://localhost:8000

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Open http://localhost:3000

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /cypher` - Extract fix from URL
- `GET /categories` - List fix categories

### Example Request

```bash
curl -X POST http://localhost:8000/cypher \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=..."}'
```

## Tech Stack

- **Backend:** Python, FastAPI, Anthropic Claude
- **Frontend:** Vanilla HTML/CSS/JS (for now)
- **Transcript:** summarize CLI
- **Hosting:** TBD (Railway, Vercel, etc.)

## Roadmap

- [x] Core extraction API
- [x] Basic web UI
- [ ] User accounts
- [ ] Save fixes library
- [ ] Community upvotes
- [ ] Mobile apps
- [ ] Verified fixes

## Team

- 🌬️ **Zephyr** - Code, AI, Architecture  
- 🔧 **Carlos** - Vision, Product, Domain Expert

---

*Built with 🔥 in 2026*

**Domain:** cypherit.ai  
**Contact:** contact@cypherit.ai
