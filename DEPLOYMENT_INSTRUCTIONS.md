# RajOS V2 Platform-Specific Deployment Instructions

## Table of Contents
1. Render Deployment (Backend + PostgreSQL)
2. Railway Deployment (Backend + SQLite/PG)
3. Netlify Deployment (Frontend only)
4. Domain Configuration
5. Post-Deployment Verification

---

## 1. Render Deployment

### Overview
Render.com offers free tier for backend services with Docker support. PostgreSQL is available add-on.

### Backend Deployment (FastAPI + Docker)

#### Step 1: Prepare Repository
Ensure these files exist in your RajOS root:
- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/.env` (production configuration)

#### Step 2: Create Render Service
1. Go to [render.com](https://render.com) and create an account
2. New Web Service → Docker
3. Repository: "Deploy a service from Docker"
4. Name: `rajos-backend`
5. Docker Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Root Directory: `./backend`
7. Enable "Auto Deploy" from GitHub repository

#### Step 3: Configure Environment Variables
In the Render dashboard → Service → Environment, add:

| Variable | Value | Description |
|---|---|---|
| `SECRET_KEY` | `your_48_byte_random_string` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `APP_NAME` | `RajOS` | Application name |
| `APP_VERSION` | `2.0.0` | Version |
| `DEBUG` | `false` | Production mode |
| `API_V1_STR` | `/api/v1` | API version prefix |
| `DATABASE_URL` | `postgresql://user:password@db.internal:5432/rajos` | From PostgreSQL add-on |
| `CORS_ORIGINS` | `https://your-frontend-domain.com` | Production frontend URL |
| `DEFAULT_LLM_PROVIDER` | `gemini` | Or `openai`/`local` |
| `GEMINI_API_KEY` | `your_gemini_key` | From AI Studio (or omit for local) |
| `OPENAI_API_KEY` | `your_openai_key` | Optional |
| `RAJOS_DEBUG` | `false` | Debug override |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | 7-day tokens |

#### Step 4: Add PostgreSQL Database
1. In Render dashboard → New → PostgreSQL
2. Name: `rajos-db`
3. Plan: Free (or Hobby for production)
4. Note the internal connection string Render provides

5. Update `DATABASE_URL` with Render's provided connection string:
   ```
   postgresql://rajos_db_user:rajos_db_password@db.internal.render.com/rajos
   ```

#### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (Dockerfile + dependencies)
3. View logs if build fails
4. Once live, note the backend URL: `https://rajos-backend.onrender.com`

#### Step 6: Set Up Custom Domain (Optional)
1. In Render → Domain → Add Custom Domain
2. Follow DNS verification steps
3. Update your domain's DNS records

### Frontend Deployment (Netlify - see Section 3)

### Health Verification
After deployment, visit:
- `https://rajos-backend.onrender.com/health`
- Should return: `{"status":"healthy","debug":false,"database":"healthy"}`
- `https://rajos-backend.onrender.com/` → Welcome message

---

## 2. Railway Deployment

### Overview
Railway offers generous free tier with persistent disks (good for SQLite) and PostgreSQL.

### Backend Deployment (FastAPI + Docker or Direct)

#### Option A: Docker Deployment

##### Step 1: Prepare Files
Ensure exists:
- `backend/Dockerfile`
- `backend/.dockerignore`
- `backend/.env` (updated production config)

##### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app) and create account
2. New Project → Deploy from Dockerfile
3. Select your RajOS repository
4. Railway will auto-detect the Dockerfile

##### Step 3: Configure Services
Railway automatically adds:
- **Web Service**: Your FastAPI app
- **PostgreSQL**: Add PostgreSQL service from sidebar

##### Step 4: Environment Variables
In Railway dashboard → Variables, add:

| Variable | Value |
|---|---|
| `SECRET_KEY` | `your_48_byte_random_string` |
| `DEBUG` | `false` |
| `DATABASE_URL` | Auto-filled by Railway PostgreSQL (or set manually) |
| `CORS_ORIGINS` | `https://your-frontend-domain.com` |
| `DEFAULT_LLM_PROVIDER` | `gemini`/`openai`/`local` |
| `GEMINI_API_KEY` | `your_key` (if using Gemini) |
| `OPENAI_API_KEY` | `your_key` (if using OpenAI) |

##### Step 5: Railway PostgreSQL Note
Railway provides persistent disk storage, making SQLite viable:
- Railway automatically provides `DATABASE_URL` env var
- SQLite file will persist across deployments
- No migration needed if using SQLite

##### Step 6: Deploy
1. Click "Deploy"
2. Railway builds Docker image
3. Application starts and is available at `railway.app` domain

#### Option B: Direct Deployment (No Docker)

##### Step 1: Railway CLI
```bash
npm install -g @railway/cli
railway login
railway init
```

##### Step 2: Set Variables
```bash
railway variables set SECRET_KEY="your_key"
railway variables set DEBUG="false"
# ... etc
```

##### Step 3: Deploy
```bash
railway up
```

### Health Verification
- `https://your-app.up.railway.app/health`
- Should return healthy status with database

---

## 3. Netlify Deployment

### Overview
Netlify for frontend (Next.js). Backend deployed separately (Render/Railway).

### Frontend Deployment

#### Step 1: Prepare Frontend
Ensure `next.config.js` has:
```javascript
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}
```

#### Step 2: Create Netlify Site
1. Go to [netlify.com](https://netlify.com) and create account
2. New Site → Deploy manually
3. Or connect GitHub repository

#### Step 3: Set Build Settings
- Build command: `next build`
- Publish directory: `.next`
- Base directory: `./Frontend`

#### Step 4: Configure Environment Variables
In Netlify dashboard → Site → Site settings → Build & deploy → Environment variables, add:

| Variable | Value | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://rajos-backend.onrender.com` (or Railway URL) | Backend API base URL |
| `NEXT_PUBLIC_APP_NAME` | `RajOS` | Application branding |

#### Step 5: Deploy
1. Click "Deploy site"
2. Wait for build to complete
3. Once live, note the frontend URL: `https://rajos-netlify.netlify.app`

#### Step 6: Verify Configuration
Visit frontend and check:
- Page loads without console errors
- API calls go to correct backend URL
- Authentication flows work

### Backend (Refer to Section 1 or 2)
Deploy Rails/Render backend first, then configure Netlify with the correct `NEXT_PUBLIC_API_URL`.

### Health Verification
- Frontend loads successfully
- Navigation between pages works
- AI Chat sends requests to backend API
- Dashboard statistics load

---

## 4. Domain Configuration

### Custom Domains for Backend (Render/Railway)

#### Render Custom Domain
1. In Render dashboard → Domain → Add Custom Domain
2. Enter: `api.rajos.app` (or your preferred subdomain)
3. Follow DNS verification:
   - Add TXT record: `_render-challenge.xxxxxx = verification-string`
   - Or add CNAME record pointing to `xxx.xxx.onrender.com`

#### Railway Custom Domain
1. In Railway dashboard → Domain → Add Domain
2. Enter: `api.rajos.app`
3. Follow automatic DNS verification

### Custom Domains for Frontend (Netlify)

#### Netlify Custom Domain
1. In Netlify dashboard → Domain → Add Custom Domain
2. Enter: `rajos.app` or `www.rajos.app`
3. Follow DNS instructions:
   - Add CNAME: `www.netlify.app`
   - Or add DNS records as instructed

### Update Environment Variables After Domain Setup
- Update `NEXT_PUBLIC_API_URL` to use new domain
- Update `CORS_ORIGINS` in backend to include new domain
- Re-deploy both frontend and backend

---

## 5. Post-Deployment Verification

### Checklist After Deployment

#### Backend Health
- [ ] `GET /health` returns `{"status":"healthy","database":"healthy"}`
- [ ] `GET /` returns welcome message with version 2.0.0
- [ ] `GET /readiness` returns database status (if endpoint exists)
- [ ] Application starts without RuntimeError (config validation)

#### Authentication
- [ ] Register new user works
- [ ] Login produces JWT token
- [ ] Protected routes ( `/tasks/`, `/chat/`, `/memory/`) return 401 without token
- [ ] Protected routes return data with valid Bearer token
- [ ] Cross-user data isolation verified (create task as user A, verify user B can't see it)

#### Critical Workflows
- [ ] Chat message endpoint works (`POST /chat/message`)
- [ ] Conversation persistence (messages stored, retrievable)
- [ ] Task creation and retrieval works
- [ ] Memory creation and search works
- [ ] Document upload and RAG search works (if using)
- [ ] Automation endpoints work (if configured)

#### Frontend
- [ ] Frontend homepage loads at deployed URL
- [ ] Navigation between pages works (dashboard, chat, tasks, etc.)
- [ ] AI Chat component works (sends/receives messages)
- [ ] Task management UI works (create, view, complete tasks)
- [ ] No critical console errors in browser dev tools
- [ ] Responsive design works (resize browser, mobile layout)
- [ ] Login/out flows work with deployed backend

#### Cross-Platform
- [ ] Frontend API calls go to correct backend URL
- [ ] CORS permits frontend origin (check browser console for CORS errors)
- [ ] Authentication cookies/tokens work across domains
- [ ] Health endpoints accessible from external IP

### Troubleshooting Common Issues

#### 1. Health endpoint returns "database: unhealthy"
- **Cause**: Database connection failed
- **Fix**: Check `DATABASE_URL` environment variable
- **Fix**: For SQLite on Render/Railway, ensure persistent disk is enabled
- **Fix**: For PostgreSQL, check connection string format

#### 2. Authentication fails (401 on protected routes)
- **Cause**: JWT token not sent or invalid
- **Fix**: Check `Authorization: Bearer <token>` header
- **Fix**: Verify `SECRET_KEY` matches between deployments
- **Fix**: Ensure `DEBUG=false` in production

#### 3. CORS errors in browser console
- **Cause**: Frontend origin not in CORS allowed list
- **Fix**: Add frontend URL to `CORS_ORIGINS` in backend `.env`
- **Fix**: Redeploy backend after changing CORS config
- **Fix**: Verify `NEXT_PUBLIC_API_URL` matches actual backend URL

#### 4. AI responses fail or use fallback
- **Cause**: LLM provider key missing or invalid
- **Fix**: Set `GEMINI_API_KEY` or change `DEFAULT_LLM_PROVIDER=local`
- **Fix**: Check API key has proper permissions
- **Fix**: Test key manually at provider console

#### 5. Frontend can't reach backend
- **Cause**: `NEXT_PUBLIC_API_URL` incorrect
- **Fix**: Verify environment variable matches actual backend URL
- **Fix**: Include protocol (https://) and port if non-standard
- **Fix**: Redeploy frontend after fixing URL

#### 6. Database migrations or table errors
- **Cause**: New tables not created
- **Fix**: On first start, app runs `Base.metadata.create_all(bind=engine)`
- **Fix**: Ensure database user has CREATE TABLE permissions
- **Fix**: Check `DATABASE_URL` format and network access

#### 7. Secrets detected in logs or frontend
- **Cause**: API keys accidentally exposed
- **Never commit `.env` files** - they're in `.gitignore`
- **Use platform secret management** (Render/Railway/Netlify dashboards)
- **Revoke and rotate** any exposed credentials immediately

### Rollback Procedure

If deployment fails or causes issues:

#### Backend Rollback
1. Render: Previous version auto-kept; switch in dashboard
2. Railway: `railway rollback` CLI command
3. Docker: `docker compose up previous-image`
4. Restore database from `docs/DATABASE_BACKUP_AND_RECOVERY.md`

#### Frontend Rollback
1. Netlify: "Deploy > Deploys" → click previous deploy → "Restore"
2. Or redeploy previous `next build` output

#### Database Rollback
1. Copy backup: `cp rajos.db.backup_20240101.db rajos.db`
2. Restart application
3. Verify data integrity

---

## Quick Deployment Summary

### Minimal Deployment (All Platforms)

1. **Backend** (Render or Railway):
   - Dockerfile + .dockerignore present
   - `.env` with: SECRET_KEY, DEBUG=false, DATABASE_URL, CORS_ORIGINS
   - Deploy and note URL

2. **Frontend** (Netlify):
   - `NEXT_PUBLIC_API_URL` set to backend URL
   - Deploy and verify

3. **Verify**:
   - `/health` endpoint healthy
   - Authentication works
   - Critical workflows (chat, tasks) functional

4. **Optional** (for production):
   - Custom domains (api.rajos.app, app.rajos.app)
   - SSL/TLS already provided by platforms
   - Monitoring/alerts setup
   - Backup configuration

---

**RajOS V2 is now prepared for deployment on any of these platforms.** Follow the steps corresponding to your chosen platform, and the application should deploy successfully with proper configuration.

The key success factors are:
- ✅ `SECRET_KEY` set to secure random value
- ✅ `DEBUG=False` in production
- ✅ `CORS_ORIGINS` matches frontend domain
- ✅ `DATABASE_URL` valid for your platform
- ✅ At least one LLM provider key configured
- ✅ `NEXT_PUBLIC_API_URL` points to real backend