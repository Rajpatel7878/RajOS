# RajOS System Architecture

> Version: 1.0
> Architecture Style: Client-Server
> Status: Planning

---

# Overview

RajOS follows a modern full-stack architecture.

Frontend communicates with the Backend through REST APIs.

The Backend processes requests, communicates with the PostgreSQL database, and returns responses to the Frontend.

---

# High Level Architecture

```
                User
                  │
                  ▼
      ┌─────────────────────┐
      │     Next.js App     │
      │ (Frontend UI/UX)    │
      └─────────────────────┘
                  │
          HTTPS REST API
                  │
                  ▼
      ┌─────────────────────┐
      │      FastAPI        │
      │ (Backend Server)    │
      └─────────────────────┘
                  │
             SQL Queries
                  │
                  ▼
      ┌─────────────────────┐
      │    PostgreSQL DB    │
      └─────────────────────┘
```

---

# Frontend Architecture

Frontend Stack

- Next.js
- React
- TypeScript
- Tailwind CSS

Folder Structure

```
frontend/

app/

components/

hooks/

lib/

services/

types/

styles/

public/
```

Responsibilities

- User Interface
- Forms
- Charts
- Dashboard
- Authentication Pages
- API Calls
- State Management

---

# Backend Architecture

Backend Stack

- FastAPI
- Python
- SQLAlchemy
- Pydantic

Folder Structure

```
backend/

app/

api/

models/

schemas/

services/

database/

middlewares/

utils/

config/

main.py
```

Responsibilities

- Authentication
- CRUD Operations
- Validation
- Business Logic
- Database Access
- Security
- API Endpoints

---

# Database Layer

Database

PostgreSQL

Responsibilities

- Store user data
- Store tasks
- Store goals
- Store projects
- Store notes
- Store analytics
- Maintain relationships

---

# Authentication Flow

```
User

↓

Login Page

↓

Backend

↓

Verify Credentials

↓

Generate JWT Token

↓

Return Token

↓

Access Protected Routes
```

---

# Dashboard Flow

```
User Opens Dashboard

↓

Frontend Requests Data

↓

Backend Receives Request

↓

Database Returns Data

↓

Backend Processes Data

↓

Frontend Displays Widgets
```

---

# Task Flow

```
Create Task

↓

Frontend Validation

↓

API Request

↓

Backend Validation

↓

Database Save

↓

Success Response

↓

Dashboard Updates
```

---

# Goal Flow

```
Create Goal

↓

Backend

↓

Database

↓

Progress Tracking

↓

Dashboard Update
```

---

# Coding Tracker Flow

```
Coding Session

↓

Save Hours

↓

Update Database

↓

Analytics Updated
```

---

# Project Flow

```
Project Created

↓

Tasks Added

↓

Progress Updated

↓

Completed

↓

Archived
```

---

# API Architecture

```
Frontend

↓

REST API

↓

FastAPI Routes

↓

Services

↓

Database

↓

Response

↓

Frontend
```

---

# Layered Architecture

```
Presentation Layer

↓

Business Logic Layer

↓

Data Access Layer

↓

Database Layer
```

---

# Error Handling

Frontend

- Form Validation
- Toast Messages
- Loading States

Backend

- HTTP Status Codes
- Exception Handling
- Validation Errors
- Logging

---

# Security

Authentication

- JWT

Authorization

- Protected Routes

Password

- Hashing

API

- Validation

Database

- Parameterized Queries

HTTPS

- Enabled

---

# Logging

Application Logs

API Logs

Database Logs

Error Logs

Future Analytics Logs

---

# Performance

- Lazy Loading
- Code Splitting
- Image Optimization
- Database Indexes
- Pagination
- Caching (Future)

---

# Scalability

RajOS is designed so new modules can be added without changing the existing architecture.

Future modules:

- AI Assistant
- Mobile App
- Team Workspace
- Offline Mode
- Cloud Sync

---

# Deployment Architecture

```
User

↓

Vercel

↓

Next.js

↓

FastAPI

↓

Railway

↓

PostgreSQL (Neon)
```

---

# Architecture Principles

- Modular Design
- Reusable Components
- Clean Code
- Separation of Concerns
- Single Responsibility
- Scalable Structure
- Maintainable Code
- Secure by Default

---

# Technology Summary

Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

Backend

- FastAPI
- Python

Database

- PostgreSQL

Deployment

- Vercel
- Railway
- Neon

Version Control

- Git
- GitHub

---

# Next Document

TechStack.md