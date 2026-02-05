# Contributing to CypherIt

First off, thank you for considering contributing to CypherIt! 🔧

We're building "TikTok for tutorials" — extracting the fix from any YouTube video in 60 seconds. Every contribution helps millions of people solve problems faster.

## 🚀 Quick Start

1. Fork the repo
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/cypherit.git`
3. Install dependencies:
   ```bash
   cd cypherit/backend
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API keys
5. Run locally:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
6. Open `frontend/index.html` in your browser

## 🎯 Ways to Contribute

### Good First Issues
Look for issues labeled `good first issue` — these are perfect for newcomers!

### Areas We Need Help
- **Prompt Engineering** — Improve extraction quality
- **Multi-LLM Support** — Add Gemini, Groq, Ollama backends
- **Frontend Polish** — Animations, mobile UX, accessibility
- **New Features** — Check the roadmap for what's coming
- **Documentation** — Tutorials, translations, examples
- **Testing** — Find edge cases, report bugs

## 📝 Pull Request Process

1. Create a branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test locally (run the health check: `bash scripts/health_check.sh`)
4. Commit with clear messages: `git commit -m "Add: description of change"`
5. Push and open a PR against `main`

### PR Guidelines
- Keep PRs focused — one feature or fix per PR
- Include screenshots for UI changes
- Update docs if needed
- Be kind in code reviews

## 🏆 Recognition

Every contributor gets:
- Listed in CONTRIBUTORS.md
- Shout-out on our socials for significant contributions
- Co-author credit for major features

## 💬 Community

- **GitHub Discussions** — Questions, ideas, show & tell
- **Issues** — Bug reports, feature requests

## 🤝 Code of Conduct

Be excellent to each other. We're all here to help people fix things faster.

- Be respectful and inclusive
- Assume good intent
- Help newcomers
- No spam, harassment, or toxicity

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Questions? Open a Discussion or reach out at contact@cypherit.ai

Let's build something useful together! 🌬️
