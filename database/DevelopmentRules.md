# RajOS Development Rules

> Version: 1.0
> Status: Active

---

# Purpose

This document defines the development standards for RajOS.

Every feature, component, API, and database change must follow these rules to ensure the project remains clean, scalable, and maintainable.

---

# 1. General Rules

- Write clean and readable code.
- Avoid unnecessary complexity.
- Keep the project modular.
- Follow consistent naming conventions.
- Never duplicate code.
- Refactor when necessary.

---

# 2. Git Rules

Commit frequently.

Commit Message Format

```
feat: add dashboard cards

fix: resolve login bug

refactor: improve task service

docs: update roadmap

style: improve sidebar UI
```

Never commit:

- Passwords
- API Keys
- Environment Variables
- Database Credentials

---

# 3. Branch Rules

Main Branch

```
main
```

Development Branch

```
dev
```

Feature Branch

```
feature/dashboard

feature/tasks

feature/auth

feature/goals
```

Bug Fix Branch

```
bugfix/login

bugfix/database
```

---

# 4. Folder Rules

Every file must belong to the correct folder.

Example

```
frontend/

components/

hooks/

pages/

services/

types/

styles/

assets/
```

Backend

```
backend/

api/

models/

schemas/

services/

database/

middlewares/

utils/
```

---

# 5. Naming Convention

Components

```
TaskCard.tsx

DashboardCard.tsx

GoalProgress.tsx
```

Hooks

```
useTasks.ts

useProjects.ts
```

API Files

```
task.py

goal.py

project.py
```

Database Models

```
Task

Goal

Project
```

---

# 6. Component Rules

Each component should:

- Have one responsibility.
- Be reusable.
- Be small and focused.
- Accept props.
- Avoid unnecessary state.

---

# 7. API Rules

Every endpoint should:

- Validate input.
- Return proper HTTP status codes.
- Handle errors.
- Return consistent JSON.

Example

```
GET /tasks

POST /tasks

PUT /tasks/{id}

DELETE /tasks/{id}
```

---

# 8. Database Rules

Every table should:

- Have a Primary Key.
- Use Foreign Keys where needed.
- Include timestamps.
- Avoid duplicate data.

Standard Columns

```
id

created_at

updated_at
```

---

# 9. UI Rules

The interface should be:

- Clean
- Modern
- Minimal
- Responsive
- Accessible
- Consistent

Use consistent:

- Colors
- Fonts
- Icons
- Spacing
- Buttons

---

# 10. Responsive Design

RajOS must work on:

- Desktop
- Laptop
- Tablet
- Mobile

---

# 11. Security Rules

Always:

- Hash passwords.
- Validate user input.
- Protect API routes.
- Use HTTPS.
- Sanitize data.
- Store secrets in environment variables.

Never:

- Store plain text passwords.
- Expose API keys.
- Trust client-side validation alone.

---

# 12. Performance Rules

Optimize:

- Images
- API calls
- Database queries
- Component rendering
- Bundle size

Use:

- Lazy Loading
- Pagination
- Memoization
- Caching (Future)

---

# 13. Error Handling

Frontend

- Loading States
- Empty States
- Friendly Error Messages

Backend

- Exception Handling
- Validation Errors
- Logging

---

# 14. Documentation Rules

Every module should include:

- Purpose
- Features
- API Endpoints
- Database Tables
- Future Improvements

Update documentation whenever major features are added.

---

# 15. Testing Rules

Before merging any feature:

- Test manually.
- Verify UI.
- Verify API.
- Check database.
- Test edge cases.

---

# 16. Code Review Checklist

Before committing:

- Code is readable.
- No duplicate logic.
- No console logs.
- No unused imports.
- Proper naming.
- No sensitive data.
- Documentation updated.

---

# 17. Development Workflow

```
Plan Feature

↓

Create Branch

↓

Develop Feature

↓

Test

↓

Commit

↓

Merge

↓

Deploy
```

---

# 18. Project Principles

RajOS should always be:

- Simple
- Fast
- Secure
- Scalable
- Reliable
- Modular
- Maintainable

Every new feature should improve the product without making it unnecessarily complicated.

---

# Development Motto

> Build with quality, improve continuously, and create a system that remains useful for years.

---

# Status

Development Rules Approved

Next Document

README.md