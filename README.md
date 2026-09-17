# RajOS — Intelligent Personal Operating System

**Version 2.0** | Python · FastAPI · Next.js · Gemini AI

RajOS is an intelligent personal workspace that combines AI chat, memory, task management, notes, documents, search, agents, and automation — all in one professional interface.

---

## 📋 Current Features

| Feature | Status |
|---------|--------|
| AI Chat (Gemini 2.5 Flash) | ✅ Working |
| Multimodal Uploads (images + docs) | ✅ Working |
| Task Management (create, complete, delete) | ✅ Working |
| Notes (create, read, delete) | ✅ Working |
| Memory Engine (pattern-based extraction) | ✅ Working |
| Dashboard Stats + Activity | ✅ Working |
| Email/Password Authentication | ✅ Working |
| Google OAuth Login | ✅ Working |
| Phone OTP Login (Fast2SMS) | ✅ Working |
| JWT Authentication (7-day token) | ✅ Working |
| Health & Readiness Endpoints | ✅ Working |
| 5 AI Agent Personas (Atlas, Nova, Sage, Echo, Pulse) | ✅ Working |
| Document Upload & RAG Pipeline | ⚠️ Partial |
| Semantic Memory Search | ⚠️ Partial |
| Automation Engine | ⚠️ Partial |
| Token Refresh | ❌ Not yet |
| Database Migrations (Alembic) | ❌ Not yet |

---

## 🧰 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 13.5 (App Router), TypeScript 5.2 |
| UI | Radix UI, Tailwind CSS, Framer Motion, Three.js |
| Backend | FastAPI 0.140, Python 3.10+ |
| Database | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy |
| Authentication | JWT (python-jose) + bcrypt |
| AI | Google Gemini 2.5 Flash |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |

---

## 📁 Project Structure

```
RajOS/
├── app/                  # FastAPI backend (primary)
│   ├── core/            # Settings, logging, security utilities
│   ├── database/        # DB engine, session, get_db()
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── routes/          # Auth + user routes
│   ├── routers/         # Feature routers (chat, tasks, notes, ...)
│   ├── services/        # Business logic
│   ├── security/        # JWT creation + get_current_user dependency
│   ├── llm/             # LLM abstraction (Gemini, OpenAI, Local)
│   ├── agents/          # Agent orchestration
│   ├── memory/          # Memory engine
│   ├── conversation/    # Conversation manager
│   ├── automation/      # Automation rules
│   ├── documents/       # Document processing
│   ├── search/          # Search router
│   ├── embeddings/      # Embedding generation
│   ├── rag/             # RAG pipeline
│   └── vector_db/       # ChromaDB adapter
├── Frontend/             # Next.js frontend
│   ├── app/             # Pages + Next.js API routes
│   ├── components/      # Shared UI components
│   ├── services/api/    # API service functions
│   ├── lib/             # Types, utilities, data
│   └── hooks/           # Custom React hooks
├── tests/               # pytest test suite
├── docs/                # Architecture documentation
│   └── RAJOS_V2_ARCHITECTURE.md
├── .env.example         # Environment variable template
├── requirements.txt     # Python dependencies
├── Dockerfile           # Backend container
└── docker-compose.yml   # Full-stack container setup
```

---

## ⚙️ Prerequisites

- **Python** 3.10 or later
- **Node.js** 18 or later + npm
- **Git**
- A **Google AI Studio API key** (for Gemini): https://aistudio.google.com/

---

## 🚀 Backend Setup

### 1. Clone the repository

```bash
git clone https://github.com/Rajpatel7878/RajOS.git
cd RajOS
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and set at minimum:

```env
# Generate a secure key:
# python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=your-generated-secret-key-here

GEMINI_API_KEY=your-google-ai-studio-key-here
DEFAULT_LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash
```

### 5. Run the backend server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **Readiness check:** http://localhost:8000/readiness

---

## 🎨 Frontend Setup

```bash
cd Frontend
npm install
```

Create `Frontend/.env`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
GEMINI_API_KEY=your-google-ai-studio-key-here
```

Run the development server:

```bash
npm run dev
```

Frontend available at: http://localhost:3000

---

## 🧪 Running Tests

```bash
# From the project root
pip install pytest pytest-cov httpx

pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=term-missing -v
```

Run TypeScript type checking:

```bash
cd Frontend
npm run typecheck
```

---

## 🐳 Docker Setup

Run the full stack with Docker Compose:

```bash
# Copy and configure environment first
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and SECRET_KEY

docker compose up --build
```

---

## 🔑 API Documentation

When the backend is running, visit http://localhost:8000/docs for interactive Swagger documentation of all endpoints.

### Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/register` | Create a new user account |
| `POST` | `/login` | Email/password authentication |
| `GET` | `/health` | Health check |
| `GET` | `/readiness` | Database readiness check |
| `GET` | `/tasks/` | List user tasks |
| `POST` | `/tasks/` | Create a task |
| `PATCH` | `/tasks/{id}/complete` | Mark task complete |
| `GET` | `/notes/` | List user notes |
| `POST` | `/notes/` | Create a note |
| `GET` | `/memory/` | List memories |
| `POST` | `/chat/message` | Send a chat message |
| `GET` | `/chat/history` | Get conversation history |
| `GET` | `/dashboard/stats` | Dashboard statistics |
| `GET` | `/dashboard/activity` | Recent activity |

---

## 🔒 Security Notes

1. **Never commit `.env`** — it is git-ignored. Use `.env.example` as the template.
2. **Generate a real `SECRET_KEY`** for production: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
3. The default `SECRET_KEY` in `.env.example` is **not secure** — it is a placeholder only.
4. **Google OAuth credentials** should only be placed in backend `.env`, never in frontend code.

---

## 📐 Architecture

See [`docs/RAJOS_V2_ARCHITECTURE.md`](docs/RAJOS_V2_ARCHITECTURE.md) for:
- Complete system architecture with Mermaid diagrams
- Request and authentication lifecycle flows
- Database schema
- LLM provider architecture
- V2 improvement roadmap

---

## ⚠️ Known Limitations

- Token refresh is not implemented — users re-authenticate every 7 days
- No database migration system (Alembic) — schema changes require manual management
- RAG pipeline is partially implemented — not fully wired into chat
- TypeScript build errors are suppressed in `next.config.js` — tsc strict mode pending
- Client-side offline JWT fallback exists in auth service (remove before production)

---

## 🗺️ V2 Roadmap

**Phase 1 (Complete):** Foundation & stability — config, secrets, testing, architecture  
**Phase 2:** Production hardening — Alembic, token refresh, rate limiting  
**Phase 3:** AI feature completion — full RAG, semantic memory, streaming  
**Phase 4:** Scale — PostgreSQL, WebSockets, PWA

---

## 📄 License

MIT License — see [LICENSE](LICENSE)
