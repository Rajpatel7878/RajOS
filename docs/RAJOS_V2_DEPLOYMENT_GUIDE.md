# RajOS V2 — Deployment Guide

## Recommended Deployment Architecture

Based on the existing RajOS V2 codebase, here is the recommended production deployment architecture:

### Architecture Overview

```
Frontend Hosting (Next.js)
    ↓
Backend API Hosting (FastAPI/UVicorn)
    ↓
Persistent Database (SQLite or PostgreSQL)
    ↓
Configured AI Providers (Gemini/OpenAI)
    ↓
Background Execution Infrastructure
```

### Frontend Hosting

**Recommended Platform**: Netlify or Vercel

**Configuration**:
- Build command: `next build`
- Publish directory: `.next`
- Environment variable: `NEXT_PUBLIC_API_URL` (set to production backend URL)
- Do NOT bundle API keys or secrets into the frontend

**Environment Variables Required**:
- `NEXT_PUBLIC_API_URL` - Production backend API base URL (e.g., `https://api.rajos.app`)
- `NEXT_PUBLIC_APP_NAME` - Application name for branding

### Backend API Hosting

**Recommended Platform**: Render, Railway, or any platform supporting Python/UVicorn

**Docker Configuration**:
- Dockerfile: `backend/Dockerfile` (already created)
- Port: `8000`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Required Environment Variables** (set in platform dashboard):
- `SECRET_KEY` - Generated with: `python -c "import secrets; print(secrets.token_urlsafe(48))"`
- `DATABASE_URL` - `sqlite:///./rajos.db` for SQLite or PostgreSQL connection string
- `DEFAULT_LLM_PROVIDER` - `gemini`, `openai`, or `local`
- `GEMINI_API_KEY` - If using Gemini provider
- `OPENAI_API_KEY` - If using OpenAI provider
- `CORS_ORIGINS` - Comma-separated list of allowed frontend origins
- `RAJOS_DEBUG` - Should be `false` in production

**Health Check Endpoint**: `GET /health`
- Returns: `{"status": "healthy", "debug": false, "database": "healthy"}`
- Used by platform for service health monitoring

### Persistent Database

**Default**: SQLite (`sqlite:///./rajos.db`)

**⚠️ Critical**: SQLite requires persistent disk storage.

**If using SQLite on these platforms**:
- ✅ Render (with persistent disks)
- ✅ Railway (with persistent disks)
- ✅ Heroku (with external storage)
- ❌ Ephemeral filesystem platforms (data lost on restart)

**If using PostgreSQL** (recommended for production):
- Use connection string: `postgresql://user:password@host:port/database`
- Configure connection pooling (pool_size=5, max_overflow=10)
- Set `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_PRE_PING` environment variables
- Enable SSL/TLS for secure connections

### AI Provider Configuration

**Currently Supported**:
1. **Gemini** (default) - Google Generative AI
2. **OpenAI** - GPT-4o, GPT-4, etc.
3. **Local** - Local LLM for development/testing

**Configuration**:
- Set `DEFAULT_LLM_PROVIDER` to desired provider
- Set the corresponding API key:
  - `GEMINI_API_KEY` from Google AI Studio
  - `OPENAI_API_KEY` from OpenAI platform
- Never expose AI provider keys to the frontend

**The application will fail at startup** if:
- `DEFAULT_LLM_PROVIDER=gemini` and `GEMINI_API_KEY` is not set
- `DEFAULT_LLM_PROVIDER=openai` and `OPENAI_API_KEY` is not set
- `SECRET_KEY` is not set (validated at import)

### CORS Configuration

**Production CORS Settings**:
- Set `CORS_ORIGINS` in backend `.env` to: `https://rajos.app,https://www.rajos.app`
- Or configure via platform environment variables
- Frontend URL must match exactly

**Current Development CORS**:
- `http://localhost:3000,http://127.0.0.1:3000`
- Too permissive for production (`r"^https?://.*"` removed)

### Health Checks

**Backend Health Endpoint**: `GET /health`
```json
{
  "status": "healthy",
  "debug": false,
  "database": "healthy"
}
```

**Platform Health Monitoring**:
- Most platforms support checking `GET /health`
- Should return 200 when healthy, 503 when unhealthy
- Use for auto-restart and load balancer health checks

### Authentication Configuration

**JWT Tokens**:
- Issued at `/login` endpoint
- Valid for `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 10080 = 7 days)
- Use `Authorization: Bearer <token>` header for protected routes

**Cookie-Based Authentication**:
- Not currently implemented; use Bearer token pattern
- If adding cookies, set `SESSION_COOKIE_SECURE=true` in production

### File Storage

**Current Implementation**:
- Documents uploaded via API, processed, and stored in database
- Vector embeddings stored in vector database (pgvector or Chroma)
- No external file storage (S3, etc.) required for V1

**If Adding External Storage**:
- Configure `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Or use Cloudflare RADOS, Google Cloud Storage
- Never commit storage credentials to git

### Environment Variable Checklist

#### Backend (.env or Platform Env Vars)
- [ ] `SECRET_KEY` - Random 48-byte string
- [ ] `DATABASE_URL` - SQLite or PostgreSQL connection
- [ ] `DEBUG` - Set to `false` for production
- [ ] `CORS_ORIGINS` - Frontend production URL(s)
- [ ] `DEFAULT_LLM_PROVIDER` - `gemini`, `openai`, or `local`
- [ ] `GEMINI_API_KEY` - If using Gemini
- [ ] `OPENAI_API_KEY` - If using OpenAI
- [ ] `RAJOS_DEBUG` - Override debug mode

#### Frontend (.env or Platform Env Vars)
- [ ] `NEXT_PUBLIC_API_URL` - Production backend URL
- [ ] `NEXT_PUBLIC_APP_NAME` - RajOS (or customize)

### Rollback Procedures

**Backend Rollback**:
1. Previous Docker image tag or Git commit
2. `docker pull previous-image:tag` or `git checkout previous-commit`
3. `docker compose down && docker compose up -d`
4. If database migration caused issue: restore from `docs/DATABASE_BACKUP_AND_RECOVERY.md`

**Frontend Rollback**:
1. Previous Netlify/Vercel deploy
2. Or deploy previous `next build` output
3. Use platform's rollback feature

**Database Rollback**:
1. Restore from backup: `cp rajos.db.backup_timestamp.db rajos.db`
2. Verify data integrity
3. Restart application

### Troubleshooting Guide

**Common Issues**:

1. **"SECRET_KEY not configured"**
   - Set `SECRET_KEY` in backend environment variables
   - Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

2. **"GEMINI_API_KEY not configured"**
   - Set `GEMINI_API_KEY` or change `DEFAULT_LLM_PROVIDER` to `local` or `openai`

3. **"CORS origin not allowed"**
   - Add frontend production URL to `CORS_ORIGINS`
   - Check that `NEXT_PUBLIC_API_URL` matches

4. **Database "unhealthy" in health endpoint**
   - Verify `DATABASE_URL` is correct
   - For SQLite: ensure persistent disk storage
   - For PostgreSQL: check connection string and network access

5. **Frontend can't connect to backend**
   - Verify `NEXT_PUBLIC_API_URL` is set correctly
   - Check CORS configuration on backend
   - Ensure backend is running and accessible

6. **Authentication fails after deployment**
   - Verify JWT `SECRET_KEY` is consistent
   - Check that cookies aren't httpOnly if expecting browser access
   - Ensure `DEBUG=False` in production

### Deployment Checklist

#### Pre-Deployment
- [ ] Backend `.env` configured with all required variables
- [ ] Frontend environment variables set (`NEXT_PUBLIC_API_URL`)
- [ ] Database backup created (`docs/DATABASE_BACKUP_AND_RECOVERY.md`)
- [ ] AI provider keys configured and tested
- [ ] CORS origins set to production frontend URL
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] SSL/TLS configured if using custom domain

#### Deployment
- [ ] Deploy backend service
- [ ] Configure persistent database
- [ ] Set all environment variables in platform dashboard
- [ ] Deploy frontend with `NEXT_PUBLIC_API_URL`
- [ ] Verify CORS permits frontend origin
- [ ] Run health checks

#### Post-Deployment
- [ ] Verify `GET /health` returns healthy
- [ ] Test authentication (register, login, protected routes)
- [ ] Test critical workflows (chat, tasks, documents)
- [ ] Verify no critical console errors in frontend
- [ ] Check logs for any startup errors
- [ ] Document deployed URLs

#### Smoke Tests
- [ ] Backend health endpoint
- [ ] API documentation accessibility
- [ ] Authentication (register, login)
- [ ] Protected endpoint access
- [ ] Database connectivity
- [ ] Chat request and response
- [ ] Conversation persistence
- [ ] Task creation and retrieval
- [ ] Search functionality