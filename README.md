# NexusAI ⚡

> **Intelligent Content & Code Generation Platform** — Production-grade AI SaaS backend built with FastAPI, PostgreSQL, Redis, and OpenAI.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## 🎯 What is NexusAI?

NexusAI is a **production-ready AI SaaS backend** that demonstrates modern Python engineering at its finest. It provides intelligent content generation (text, code, analysis, summaries) via a robust REST + WebSocket API, with full authentication, quota management, and background processing.

Built as a **portfolio-grade project** to showcase expertise in:
- Async Python architecture (FastAPI + asyncio)
- AI integration (OpenAI GPT-4o)
- Production infrastructure (Docker, PostgreSQL, Redis, Celery)
- Security best practices (JWT, RBAC, rate limiting)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         NexusAI Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  Client (React/curl/SDK)                                        │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────┐    ┌─────────────┐    ┌──────────────────┐   │
│  │   FastAPI    │───▶│Rate Limiter │───▶│   JWT Auth       │   │
│  │   (async)    │    │ (sliding    │    │   Middleware      │   │
│  └──────┬───────┘    │  window)    │    └──────────────────┘   │
│         │            └─────────────┘                            │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API Endpoints                           │   │
│  │  /auth  /users  /generate  /admin  /ws/chat              │   │
│  └──────────────┬──────────────────────────┬────────────────┘   │
│                 │                          │                     │
│         ┌───────▼──────┐         ┌────────▼────────┐           │
│         │  AI Service  │         │  User Service    │           │
│         │  (OpenAI)    │         │  (Quota/CRUD)    │           │
│         └───────┬──────┘         └────────┬────────┘           │
│                 │                          │                     │
│         ┌───────▼──────┐         ┌────────▼────────┐           │
│         │  PostgreSQL  │         │     Redis        │           │
│         │  (SQLAlchemy │         │  (Cache + Queue) │           │
│         │   async)     │         └─────────────────┘           │
│         └──────────────┘                                        │
│                                                                  │
│  Background: Celery Worker + Beat (token reset, digests)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **JWT Auth** | Access + refresh token pair, BCrypt passwords |
| 👥 **RBAC** | Admin / User roles with protected endpoints |
| 🤖 **AI Generation** | Text, Code, Analysis, Summary via GPT-4o |
| 🌊 **Streaming** | Real-time token streaming via SSE + WebSocket |
| 💬 **Conversation Threads** | Multi-turn chat with persistent memory |
| 📊 **Token Quotas** | Per-plan monthly limits (Free/Pro/Enterprise) |
| 🛡️ **Rate Limiting** | Sliding window per user/plan tier |
| 🔑 **API Keys** | Programmatic access with secure key generation |
| ⚙️ **Background Jobs** | Celery: monthly resets, bulk processing, digests |
| 📖 **Auto Docs** | Swagger UI + ReDoc out of the box |
| 🐳 **Docker** | Full compose stack (API, DB, Redis, Celery, Flower) |
| 🧪 **Tests** | Integration + unit tests with pytest-asyncio |
| 📓 **Notebook** | Jupyter explorer for API + analytics charts |

---

## 🚀 Quick Start

### Option A: Docker (recommended)

```bash
git clone https://github.com/yourname/nexus-ai.git
cd nexus-ai

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Launch everything
cd docker && docker-compose up -d

# Check status
docker-compose ps
```

API available at: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**  
Flower dashboard: **http://localhost:5555**

---

### Option B: Local Development

```bash
# 1. Clone and create venv
git clone https://github.com/yourname/nexus-ai.git
cd nexus-ai
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL and Redis (via Docker)
cd docker && docker-compose up -d db redis && cd ..

# 4. Configure environment
cp .env.example .env
# Add OPENAI_API_KEY to .env

# 5. Run the API
uvicorn app.main:app --reload --port 8000

# 6. Seed sample data (optional)
python scripts/dev.py seed

# 7. Run tests
pytest -v
```

---

## 📡 API Reference

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","username":"yourname","password":"StrongPass1"}'

# Login → get tokens
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email":"you@example.com","password":"StrongPass1"}'

# Use token
export TOKEN="eyJ..."
```

### AI Generation

```bash
# Generate text
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing in simple terms",
    "type": "text"
  }'

# Generate code
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Python binary search with type hints",
    "type": "code"
  }'

# List my generations
curl http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $TOKEN"
```

### WebSocket Chat

```javascript
// Connect
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws/chat?token=${ACCESS_TOKEN}`
);

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === "token") process.stdout.write(msg.data);
};

// Send message
ws.send(JSON.stringify({ prompt: "Hello!", type: "text" }));
```

---

## 🗂️ Project Structure

```
nexus-ai/
│
├── app/
│   ├── main.py                    # FastAPI app factory + lifespan
│   ├── api/v1/
│   │   └── endpoints/
│   │       ├── auth.py            # Register, login, refresh, /me
│   │       ├── generation.py      # AI generate, stream, list, delete
│   │       ├── users.py           # Profile, stats, API keys
│   │       ├── admin.py           # Admin CRUD + platform stats
│   │       └── websocket.py       # Real-time chat
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (env-driven)
│   │   ├── security.py            # JWT + BCrypt
│   │   ├── deps.py                # FastAPI dependencies (auth guards)
│   │   ├── celery_app.py          # Celery configuration
│   │   └── tasks.py               # Background tasks
│   ├── models/models.py           # SQLAlchemy ORM models
│   ├── schemas/schemas.py         # Pydantic v2 request/response schemas
│   ├── services/
│   │   ├── ai_service.py          # OpenAI wrapper + streaming
│   │   ├── user_service.py        # User CRUD + quota management
│   │   └── generation_service.py  # Generation orchestration
│   ├── db/session.py              # Async engine + session factory
│   └── middleware/rate_limit.py   # Sliding window rate limiter
│
├── tests/
│   ├── test_api.py                # Integration tests (full HTTP)
│   └── unit/test_security.py     # Unit tests (JWT, hashing, schemas)
│
├── notebooks/api_explorer.ipynb   # Interactive API + analytics
├── scripts/dev.py                 # Dev automation (setup, seed, health)
├── docker/
│   ├── Dockerfile                 # Multi-stage production build
│   └── docker-compose.yml         # Full stack (API, DB, Redis, Celery)
├── .env.example
├── requirements.txt
└── pyproject.toml                 # pytest + coverage config
```

---

## 🌐 Deployment

### Railway (Recommended — free tier available)

```bash
# Install Railway CLI
npm i -g @railway/cli && railway login

# Deploy
railway new
railway add postgresql redis
railway up

# Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production
```

### Render

1. Connect GitHub repo at render.com/new
2. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add PostgreSQL + Redis from Render dashboard
4. Set env vars (OPENAI_API_KEY, SECRET_KEY, DATABASE_URL)

### Docker (VPS/AWS/GCP)

```bash
docker build -f docker/Dockerfile -t nexusai:latest .
docker run -d -p 8000:8000 --env-file .env nexusai:latest
```

---

## 🧪 Testing

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_api.py -v

# Run only unit tests (no DB needed)
pytest tests/unit/ -v

# Coverage report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 📓 Analytics Notebook

```bash
jupyter notebook notebooks/api_explorer.ipynb
```

The notebook lets you:
- Register/login interactively
- Generate content and inspect responses
- Visualize token usage with pie charts
- Plot generation history and type distribution

---

## 🗺️ Roadmap

| Feature | Status |
|---|---|
| Core API + Auth | ✅ Done |
| AI Generation (4 types) | ✅ Done |
| WebSocket streaming | ✅ Done |
| Rate limiting | ✅ Done |
| Background jobs | ✅ Done |
| Alembic migrations | 🔜 Next |
| Email verification | 🔜 Next |
| Stripe billing integration | 🔜 Planned |
| React dashboard frontend | 🔜 Planned |
| Vector DB (RAG) | 🔜 Planned |
| Fine-tuned model support | 🔜 Planned |
| Multi-tenant workspaces | 🔜 Planned |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Python 3.11+ |
| **Framework** | FastAPI 0.115 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 16 |
| **Cache/Queue** | Redis 7 |
| **Background** | Celery 5 + Flower |
| **AI** | OpenAI GPT-4o-mini |
| **Auth** | JWT (PyJWT) + BCrypt |
| **Validation** | Pydantic v2 |
| **Testing** | pytest-asyncio + httpx |
| **Deploy** | Docker + Railway/Render |

---

## 📄 License

MIT © 2025 NexusAI
