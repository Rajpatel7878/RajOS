# 🚀 RajOS – AI Personal Operating System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### 🧠 Your AI-Powered Personal Operating System

*Memory • Chat • Tasks • Notes • Authentication • RAG • AI Agent*

---

⭐ **If you like this project, consider giving it a Star!**

</div>

---

# 📖 Overview

RajOS is an AI-powered Personal Operating System built using **FastAPI** and modern AI technologies.

It combines:

- 🔐 Secure Authentication
- 🧠 AI Memory
- 💬 Intelligent Chat
- 📄 Document Intelligence
- 🔍 Semantic Search
- 🤖 Retrieval-Augmented Generation (RAG)
- 📋 Task Management
- 📝 Notes
- 🚀 AI Agent Architecture

The long-term vision is to evolve RajOS into a complete AI assistant capable of remembering users, understanding documents, planning tasks, and executing intelligent workflows.

---

# ✨ Current Features

## Authentication

- JWT Authentication
- Password Hashing
- Protected Routes
- Login
- Registration

---

## User Management

- User Profile
- Password Update
- Secure Sessions

---

## Productivity

- Task Management
- Notes Management
- AI Memory

---

## AI

- AI Chat
- Conversation History
- Document Upload
- RAG Pipeline
- Semantic Search
- Vector Database

---

# 🏗 Architecture

```
                    RajOS

                     User
                       │
         ┌─────────────┼──────────────┐
         │             │              │
         ▼             ▼              ▼
 Authentication     AI Chat       Documents
         │             │              │
         └─────────────┼──────────────┘
                       ▼
                Memory Engine
                       │
                       ▼
               RAG Processing
                       │
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
 Chunking        Embeddings       ChromaDB
                       │
                       ▼
                 AI Response
```

---

# 📂 Project Structure

```
RajOS/
│
├── app/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── security/
│   ├── rag/
│   ├── middleware/
│   ├── repositories/
│   ├── utils/
│   └── main.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI |
| Language | Python |
| ORM | SQLAlchemy |
| Database | SQLite |
| Authentication | JWT |
| Password Security | Passlib |
| AI | Sentence Transformers |
| Vector Database | ChromaDB |
| API Docs | Swagger |

---

# 🚀 Modules Completed

| Module | Status |
|---------|--------|
| Authentication | ✅ |
| User Management | ✅ |
| Tasks | ✅ |
| Notes | ✅ |
| Memory | ✅ |
| AI Chat | ✅ |
| RAG | ✅ |

---

# 🚧 Roadmap

## Phase 1 ✅

- [x] Authentication
- [x] User Management
- [x] Notes
- [x] Tasks
- [x] Memory
- [x] AI Chat
- [x] RAG

---

## Phase 2 🚀

- [ ] AI Agent
- [ ] Tool Calling
- [ ] Multi-Step Planning
- [ ] Autonomous Workflows
- [ ] Plugin System

---

## Phase 3 🌍

- [ ] Voice Assistant
- [ ] Calendar Integration
- [ ] Gmail Integration
- [ ] WhatsApp Integration
- [ ] Mobile App
- [ ] Cloud Deployment

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Rajpatel7878/RajOS.git
cd RajOS/backend
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Server

```bash
uvicorn app.main:app --reload
```

---

## Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

# 📸 Screenshots

Coming Soon

- Login
- Dashboard
- Chat
- Tasks
- Notes
- RAG Search

---

# 📈 Future Vision

RajOS aims to become an AI Operating System capable of:

- Understanding users
- Remembering conversations
- Searching knowledge
- Automating workflows
- Managing productivity
- Acting as a personal AI assistant

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Developer

## Raj Patel

Computer Science Engineering Student

Building intelligent AI systems with Python, FastAPI, and Generative AI.

GitHub:

https://github.com/Rajpatel7878

---

<div align="center">

## ⭐ Star this repository if you found it useful!

**Building RajOS — One Module at a Time 🚀**

</div>




