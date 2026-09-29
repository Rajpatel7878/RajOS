# 🧠 RajOS V2

> **Your Personal AI Operating System for Work, Knowledge, Productivity & Automation.**

RajOS is a personal AI-powered operating system designed to bring **conversation, memory, knowledge, tasks, tools, agents, productivity intelligence, and automation** into one unified workspace.

RajOS V2 evolves the project from a collection of independent features into an integrated AI system that can **understand context, remember useful information, retrieve knowledge, use tools, execute controlled actions, operate specialized agents, and intelligently assist with daily productivity.**

---

## 🚀 Vision

RajOS is being built around one core idea:

> **An AI that doesn't just answer questions — it understands your workspace and helps you get things done.**

Instead of switching between separate applications for:

* Tasks
* Notes
* Documents
* Knowledge
* Search
* AI Chat
* Memory
* Productivity
* Automation

RajOS brings them together into a single intelligent workspace.

```text
                    ┌──────────────────────┐
                    │        RajOS         │
                    │   Personal AI OS     │
                    └──────────┬───────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │
       ▼                       ▼                       ▼
  AI & Agents             Knowledge               Productivity
       │                       │                       │
       ├── AI Core             ├── Documents           ├── Tasks
       ├── Conversations       ├── RAG                 ├── Planning
       ├── Memory              ├── Search              ├── Analytics
       ├── Tools               └── Semantic Search     └── Insights
       │
       └────────────────────────────────────────────────┐
                                                        ▼
                                                  Automation
```

---

# ✨ RajOS V2

RajOS V2 is organized into **14 major development phases**.

| Phase | System                                 | Status |
| ----- | -------------------------------------- | ------ |
| 01    | V2 Foundation & Architecture           | 🔄     |
| 02    | AI Core & LLM Integration              | 🔄     |
| 03    | Conversation Intelligence 2.0          | 🔄     |
| 04    | Memory 2.0                             | 🔄     |
| 05    | Knowledge Base & RAG 2.0               | 🔄     |
| 06    | Tool Registry & Function Calling 2.0   | 🔄     |
| 07    | AI Agent System 2.0                    | 🔄     |
| 08    | Productivity Intelligence              | 🔄     |
| 09    | Automation Engine 2.0                  | ⏳      |
| 10    | Search & Unified Workspace             | ⏳      |
| 11    | Professional Frontend 2.0              | ⏳      |
| 12    | Streaming, Realtime & UX               | ⏳      |
| 13    | Security, Reliability & Testing        | ⏳      |
| 14    | Deployment, Documentation & V2 Release | ⏳      |

> 🔄 = Active V2 development
> ⏳ = Planned

---

# 🏗️ Architecture

RajOS V2 follows a layered architecture.

```text
                         ┌───────────────────────┐
                         │      RajOS Frontend   │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       API Layer       │
                         └───────────┬───────────┘
                                     │
             ┌───────────────────────┼───────────────────────┐
             │                       │                       │
             ▼                       ▼                       ▼
      Conversation              Agent System          Productivity
      Intelligence                                      Intelligence
             │                       │                       │
             └───────────────┬───────┴───────────────────────┘
                             │
                             ▼
                       ┌───────────┐
                       │  AI Core  │
                       └─────┬─────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       Memory              RAG              Tools
          │                  │                  │
          │                  │                  ▼
          │                  │           Tool Registry
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │   Services    │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │    SQLite     │
                     │   Database    │
                     └───────────────┘
```

---

# 🧩 Core Systems

## 🤖 AI Core

Centralized AI/LLM infrastructure supporting multiple providers.

Responsibilities include:

* LLM provider abstraction
* Model routing
* Generation configuration
* AI response normalization
* Error handling
* Provider health
* Usage tracking
* Streaming foundation

---

## 💬 Conversation Intelligence

RajOS conversations are persistent workspaces rather than temporary chats.

Capabilities include:

* Persistent conversations
* Conversation history
* Context management
* Conversation metadata
* Conversation search
* Titles
* Archive/restore
* Context-window management
* AI context construction

---

## 🧠 Memory

RajOS can maintain useful long-term context through its Memory system.

Memory architecture supports:

* Memory storage
* Memory retrieval
* Relevance
* Recency
* Importance
* Deduplication
* Conflict handling
* Explicit memory actions
* User-controlled memory

RajOS should store useful information rather than blindly storing every conversation.

---

## 📚 Knowledge & RAG

RajOS includes a knowledge system for working with user-provided information.

Pipeline:

```text
Document
   ↓
Ingestion
   ↓
Parsing
   ↓
Chunking
   ↓
Embedding
   ↓
Vector Storage
   ↓
Retrieval
   ↓
Reranking
   ↓
Context
   ↓
AI Response
```

Designed for:

* Documents
* Notes
* Personal knowledge
* Semantic search
* Grounded AI answers
* Source-aware responses

---

## 🛠️ Tool Registry

RajOS AI can interact with the application through a controlled Tool Registry.

Architecture:

```text
AI
 ↓
Tool Decision
 ↓
Permission Check
 ↓
Input Validation
 ↓
Tool Registry
 ↓
Tool Execution
 ↓
Result
 ↓
AI
```

Examples of potential tools:

* Task management
* Notes
* Memory
* Knowledge search
* Workspace search
* Documents
* Productivity
* Automation

RajOS does **not** allow unrestricted AI-generated code execution.

---

## 🤖 AI Agents

RajOS V2 introduces specialized AI agents.

Initial agent architecture includes:

### General Assistant

General-purpose RajOS AI.

### Productivity Agent

Focused on:

* Tasks
* Planning
* Notes
* Productivity
* Workload

### Knowledge Agent

Focused on:

* Documents
* Knowledge retrieval
* RAG
* Search
* Grounded answers

Agents operate through controlled capabilities and the Tool Registry.

---

# 📊 Productivity Intelligence

Phase 8 transforms RajOS from a task manager into an intelligent productivity system.

RajOS can analyze:

* Overdue tasks
* Upcoming deadlines
* Important tasks
* Task workload
* Stale tasks
* Quick wins
* Task dependencies
* Completion history
* Productivity trends

Potential capabilities:

```text
"What should I work on today?"

"What's overdue?"

"Plan my day."

"Break this task down."

"How productive was I this week?"

"Why are you recommending this task?"
```

Recommendations are based on actual RajOS data.

---

# ⚙️ Automation

Phase 9 will expand RajOS into an event-driven automation system.

Planned capabilities include:

* Scheduled tasks
* Recurring actions
* Deadline triggers
* Productivity briefs
* Automated workflows
* Event-based actions
* Conditional automation
* Agent-triggered workflows

---

# 🔎 Unified Search

RajOS V2 will provide a unified search layer across the workspace.

Potential search targets:

```text
Tasks
Notes
Documents
Conversations
Memories
Knowledge
Agents
Workspace data
```

The goal is to make the entire RajOS workspace searchable from one place.

---

# 🎨 Frontend

RajOS uses a professional workspace-style interface.

Planned core navigation:

```text
Workspace
├── Dashboard
├── AI Chat
└── Agents

Knowledge
├── Memory
├── Documents
└── Knowledge

Productivity
├── Tasks
├── Analytics
└── Automations

System
└── Settings
```

The frontend communicates with the FastAPI backend through centralized API services.

---

# 🧰 Tech Stack

## Backend

* Python
* FastAPI
* Pydantic
* SQLite
* SQLAlchemy / project database layer
* REST APIs

## AI

* Gemini
* OpenAI-compatible architecture
* Local LLM support
* Provider abstraction
* RAG
* Embeddings
* Vector search

## Frontend

* React
* TypeScript
* Modern component architecture
* API service layer
* Responsive UI

## Development

* VS Code
* Git
* GitHub
* Git Bash
* Antigravity

---

# 📁 Project Structure

The architecture continues to evolve throughout V2.

A simplified representation:

```text
RajOS/
│
├── backend/
│   └── app/
│       ├── agents/
│       ├── automation/
│       ├── conversation/
│       ├── documents/
│       ├── llm/
│       ├── memory/
│       ├── models/
│       ├── notifications/
│       ├── productivity/
│       ├── rag/
│       ├── resolver/
│       ├── routers/
│       ├── search/
│       ├── tools/
│       └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   └── ...
│
├── docs/
│
├── .env.example
├── README.md
└── ...
```

> The exact structure may evolve as RajOS V2 progresses.

---

# 🔐 Security Principles

Security is a core requirement of RajOS.

RajOS V2 follows these principles:

* Authentication for protected resources
* User data isolation
* Server-side authorization
* Tool permission controls
* Confirmation for risky actions
* Input validation
* Structured errors
* No unrestricted code execution
* No arbitrary database access by AI
* No secrets in logs
* No API keys committed to Git
* Prompt-injection defenses
* Controlled agent execution

AI-generated decisions never override backend security controls.

---

# 🧪 Testing

RajOS V2 is being developed with testing across multiple layers.

```text
Unit Tests
    ↓
Service Tests
    ↓
API Tests
    ↓
Integration Tests
    ↓
Security Tests
    ↓
Frontend Verification
```

Important integration paths include:

```text
User
 ↓
Conversation
 ↓
Agent
 ↓
AI Core
 ↓
Tool Registry
 ↓
Service
 ↓
Database
 ↓
Result
 ↓
AI
 ↓
User
```

---

# 🛠️ Local Development

## Clone

```bash
git clone https://github.com/Rajpatel7878/RajOS.git
cd RajOS
```

## Backend

```bash
cd backend
```

Create/activate the project's Python environment according to the current environment configuration.

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

## Frontend

From the frontend directory:

```bash
cd frontend
npm install
npm run dev
```

The development URL will be shown by the frontend development server.

---

# 🔑 Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Configure the required AI provider and application settings.

Never commit:

```text
.env
API keys
access tokens
private credentials
```

---

# 🔄 Development Workflow

RajOS V2 is developed incrementally.

Typical workflow:

```text
1. Inspect existing system
        ↓
2. Plan architecture
        ↓
3. Implement feature
        ↓
4. Test backend
        ↓
5. Test frontend
        ↓
6. Review diff
        ↓
7. Commit
        ↓
8. Push
```

Example:

```bash
git status
git diff --stat
git add .
git commit -m "Build RajOS V2 productivity intelligence"
git push
```

Commit messages should describe the change clearly.

---

# 🗺️ V2 Roadmap

## Phase 1 — Foundation

Establish the architecture required for RajOS V2.

## Phase 2 — AI Core

Create a reliable multi-provider AI architecture.

## Phase 3 — Conversation Intelligence

Turn conversations into persistent AI workspaces.

## Phase 4 — Memory 2.0

Build intelligent long-term contextual memory.

## Phase 5 — Knowledge & RAG

Create a powerful personal knowledge retrieval system.

## Phase 6 — Tools

Allow AI to safely perform controlled actions.

## Phase 7 — Agents

Create specialized AI agents capable of multi-step execution.

## Phase 8 — Productivity Intelligence

Understand tasks, workload, deadlines, planning, and productivity.

## Phase 9 — Automation

Connect intelligence with scheduled and event-driven workflows.

## Phase 10 — Unified Workspace

Unify search and workspace interactions.

## Phase 11 — Professional Frontend

Polish the complete RajOS user experience.

## Phase 12 — Realtime

Add streaming and realtime interactions.

## Phase 13 — Reliability

Strengthen security, testing, observability, and reliability.

## Phase 14 — Release

Prepare RajOS V2 for deployment and public release.

---

# 🎯 Long-Term Goal

The long-term goal of RajOS is to become a personal AI workspace that can:

```text
Understand
   ↓
Remember
   ↓
Retrieve
   ↓
Reason
   ↓
Plan
   ↓
Act
   ↓
Learn from useful context
   ↓
Automate
```

while keeping the user in control of important actions and personal data.

---

# 🌟 RajOS Philosophy

RajOS is built around five principles:

### 1. Intelligence

AI should understand context rather than simply generate text.

### 2. Action

AI should be capable of safely performing useful tasks.

### 3. Memory

Useful long-term context should improve future interactions.

### 4. Control

The user remains in control of important actions and data.

### 5. Reliability

Every intelligent feature should be backed by deterministic systems, validation, permissions, and testing.

---

# 📌 Project Status

**RajOS V2 is actively under development.**

The architecture is being implemented incrementally across the 14-phase roadmap.

The current development focus is:

> **Phase 8 — Productivity Intelligence**

Next:

> **Phase 9 — Automation Engine 2.0**

---

# 👨‍💻 Author

**Raj Patel**

B.Tech CSE

GitHub:

`Rajpatel7878`

---

# ⭐ Contributing

RajOS is currently primarily developed as a personal project.

As the V2 architecture stabilizes, contribution guidelines and development documentation will be expanded.

---

# 📄 License

License information will be added as the project approaches its public release.
