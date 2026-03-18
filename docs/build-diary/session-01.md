# Session 1 — Environment Setup & Project Scaffolding
**Date:** 2026-03-17
**Phase:** 1 (Foundation)
**Tasks completed:** Task 0 (Environment Setup), Task 1 (Project Scaffolding)

---

## What We Did

### Task 0: Environment Setup
Verified and installed all development tools on macOS:
- **Already installed:** Homebrew 5.0.16, Python 3.12.2, pip 24.0, Git 2.39.3, Docker 25.0.3, Docker Compose v2.24.5
- **Newly installed:** Ollama 0.18.1 with Llama 3.1 8B model
- **Created:** GitHub repo (Faranmo/regflow-ai), cloned locally

Verified Ollama's OpenAI-compatible API endpoint works — this is the key
architectural decision that lets us swap to Azure OpenAI later with zero
code changes (just URL + key swap).

### Task 1: Project Scaffolding
Created the full project directory structure from the master plan:
- 14 source code packages (agents, rag, ml, api, security, etc.)
- 4 test directories (unit, integration, adversarial, e2e)
- 4 prompt version directories (one per agent)
- Documentation structure (build diary, ADRs, runbooks)
- Data directories for future phases

Created project configuration files:
- Full-stack .gitignore (Python + Node.js + Docker + IDE + macOS)
- pyproject.toml with Phase 1 dependencies and tool configs
- .env.example template for environment variables
- Security plan document (rate limiting, RLS, IDOR, prompt injection)

---

## Key Decisions Made

| Decision | Reasoning |
|----------|-----------|
| Ollama for local dev | Free, OpenAI-compatible API, zero code changes when switching providers |
| pyproject.toml over requirements.txt | Modern Python standard, single file for deps + tool config |
| Security plan documented in Phase 1 | Shows security-first mindset even before implementing — financial services expectation |
| Build diary added | Portfolio differentiator — shows thought process, not just final code |
| Phase 1 deps only in pyproject.toml | Install what you need when you need it, not everything upfront |

## What I Learned

- **Homebrew** is macOS's package manager — installs dev tools via CLI
- **.gitignore** prevents secrets and cache files from being pushed to GitHub
- **MIT License** is the most permissive open-source license — best for portfolio projects
- **`__init__.py`** files tell Python a directory is an importable package
- **pyproject.toml** is the modern single-file replacement for setup.py + requirements.txt
- **`.env.example`** shows required env vars without exposing actual secrets
- **Ollama's OpenAI-compatible API** means coding to an interface — swap providers by changing URL

## Problems Encountered
- None — clean setup on macOS with most tools pre-installed

## Next Steps
- Task 2: Config & Core Utilities (config.py, errors.py, retry.py)
- Task 3: Structured Logging (structlog setup)
- Task 4: FastAPI Skeleton + Middleware (health endpoint, rate limiting, auth)
