# RajOS V2 — Personal AI Operating System

## Version
**2.0.0**

## Release Date
November 24, 2026

## Overview
RajOS V2 is a complete rewrite and expansion of the original RajOS AI operating system. It introduces a modular architecture with specialized AI agents, long-term memory, RAG knowledge retrieval, automation workflows, and unified search across all data types.

## Major Implemented Features

### AI Core & LLM Providers
- **Multi-LLM Engine**: Routes requests across GPT-4o, Claude, Gemini, and local models
- **Smart Routing**: Automatic model selection based on task complexity
- **Automatic Fallback**: Falls back to local model if configured provider fails
- **3 Provider Support**: Gemini, OpenAI, and local LLM modes

### Conversation Intelligence
- **Conversation Management**: Full CRUD with archiving and search
- **Context Awareness**: Remembers conversation context across exchanges
- **Intent Detection**: Identifies user intent (notes, tasks, documents, memories)
- **Conversation Search**: Full-text search across all conversations

### Memory Engine (2.0)
- **Deduplication**: Same key, updated value triggers conflict resolution
- **Explicit Intent Parsing**: `Remember` and `Forget` commands
- **User Data Isolation**: Strict per-user memory boundaries
- **Memory Statistics**: Count and analysis of stored memories

### RAG Knowledge System
- **Document Upload**: Process and index documents with embeddings
- **Vector Search**: Semantic search with source citations
- **Knowledge Base**: Persistent semantic search across uploaded documents
- **Chunking & Embedding**: Automatic text chunking and embedding generation

### Tool Registry & Agents
- **5 Specialized Agents**:
  - **Atlas**: General orchestrator, task planning
  - **Nova**: Knowledge agent, search and research
  - **Sage**: Planning and automation agent
  - **Echo**: Memory and preference agent
  - **Pulse**: Analytics and statistics agent
- **Tool Execution**: Each agent has specific allowed tools with permission enforcement
- **Agent Registry**: Per-user custom agent registration and isolation

### Automation Engine (2.0)
- **Trigger Types**: Schedule, interval, onetime, event-driven
- **Condition Engine**: Field evaluation with comparison operators
- **Workflow Execution**: Agent tasks, notes, notifications
- **Failure Policies**: `stop` or `continue` on action failure
- **Execution Key Idempotency**: Same key runs only once

### Unified Search
- **Cross-Domain Search**: Search conversations, documents, memories, tasks
- **Multiple Search Types**: `all`, `conversations`, `documents`, `memories`, `tasks`
- **Fuzzy/Relevance Ranking**: Results ranked by relevance

### Productivity Intelligence
- **Task Management**: Full CRUD with priorities, due dates, completion tracking
- **Task Summaries**: Counts of total, completed, pending, overdue, due today
- **User Data Isolation**: Tasks isolated per user
- **Push Notifications**: SMS via Twilio/Fast2SMS for task updates

### Dashboard & Statistics
- **Real-time Stats**: Tasks, notes, memories counts
- **Activity Feed**: Recent tasks, notes, and memories
- **Dashboard Metrics**: Overdue, due today, completion rates

### Security & Authentication
- **JWT-based Authentication**: Access tokens with expiration
- **Password Hashing**: bcrypt with CryptContext
- **User Data Isolation**: Strict per-user data boundaries
- **Google OAuth**: Integration with Supabase Google sign-in
- **Phone OTP Authentication**: 6-digit verification codes via SMS
- **Role-Based Access**: Authenticated routes require valid JWT

### Streaming & Realtime
- **SSE/Streaming Endpoints**: AI response streaming
- **WebSocket Support**: Real-time communication (architecture ready)
- **Connection Resilience**: Automatic reconnection handling

### Notifications
- **SMS Notifications**: Task creation/completion via Twilio or Fast2SMS
- **Push Subscriptions**: Web push for mobile notifications
- **Email Integration**: Configured via service settings

## Improvements (V2 vs V1)

- Complete agent framework with 5 specialized agents
- RAG knowledge system with vector embeddings
- Memory deduplication and explicit intent handling
- Automation engine with condition-based triggers
- Unified search across all data domains
- Enhanced productivity dashboard with summaries
- Professional frontend with 3D spatial interface
- Production-ready configuration and deployment guides
- Comprehensive documentation suite
- Strict user data isolation across all features

## API Changes (V2)

### New Endpoints
- `POST /chat/message` - Send message with agent routing
- `GET /chat/history` - List user conversations
- `DELETE /chat/history` - Delete all conversations
- `GET /chat/conversations/{id}` - Get conversation detail
- `PATCH /chat/conversations/{id}` - Rename/Archive conversation
- `DELETE /chat/conversations/{id}` - Delete conversation
- `GET /chat/search` - Search conversations
- `POST /memory/` - Create memory entry
- `GET /memory/` - List memories
- `DELETE /memory/{id}` - Delete memory
- `POST /memory/process` - Process memory intents
- `POST /memory/search` - Search memories
- `GET /memory/stats` - Get memory statistics
- `POST /documents/` - Upload and process document
- `GET /documents/` - List user documents
- `GET /documents/{id}` - Get document
- `PUT /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document
- `POST /documents/search` - Search documents via RAG
- `POST /tasks/` - Create task
- `GET /tasks/` - List tasks with filters
- `GET /tasks/{id}` - Get specific task
- `PATCH /tasks/{id}` - Update task
- `PATCH /tasks/{id}/complete` - Mark task completed
- `PATCH /tasks/{id}/toggle` - Toggle task completion
- `DELETE /tasks/{id}` - Delete task
- `GET /tasks/summary` - Get task summary statistics
- `POST /automation/` - Create automation
- `GET /automation/` - List automations
- `GET /automation/{id}` - Get specific automation
- `PUT /automation/{id}` - Update automation
- `DELETE /automation/{id}` - Delete automation
- `POST /automation/{id}/execute` - Execute automation
- `GET /automation/{id}/runs` - Get automation run history
- `GET /automation/{id}/preview` - Get automation preview
- `POST /automation/event` - Fire event for automations
- `GET /dashboard/stats` - Get dashboard statistics
- `GET /dashboard/activity` - Get recent activity
- `GET /health` - Health check with database status
- `GET /` - Root endpoint with app info

### Modified Endpoints
- Enhanced authentication with proper token validation
- Improved conversation management with archive support
- Better memory CRUD with deduplication logic
- Enhanced document processing with vector embeddings

### Deprecated (V1 to V2)
- Some V1 endpoints may have been restructured; check API docs for exact mappings

## Database Changes (V2)

### New Tables
- `automations` - Automation definitions and configurations
- `agent_definitions` - Custom agent registrations
- `push_subscriptions` - Web push notification subscriptions
- `search_history` - Search query logging

### Enhanced Tables
- `memories` - Enhanced with deduplication and type fields
- `documents` - Enhanced with content processing pipeline
- `conversations` - Enhanced with archiving support

### Migration Notes
- Existing SQLite database (`rajos.db`) will be auto-migrated
- All existing user data preserved (tasks, conversations, notes, memories)
- New columns added with defaults; no data loss
- Run `python -m app.main` to auto-create new tables on first start

## Security Improvements (V2)

- **JWT Configuration**: Secret key validated at startup (no hardcoded secrets)
- **CORS**: Properly configured for production (no wildcard `r"^https?://.*"`)
- **Debug Mode**: Disabled by default in production
- **User Data Isolation**: Strict per-user boundaries enforced across all endpoints
- **Password Security**: bcrypt hashing with proper context
- **Secret Management**: Environment variables never committed to git
- **Input Validation**: Pydantic schemas validate all API inputs
- **Rate Limiting**: Basic protection against abuse (configurable)

## Known Limitations

### Current Scope
- **SQLite only** on platforms without persistent disk (see deployment guide)
- **Gemini API required** unless OpenAI key or local LLM configured
- **No external file storage** (S3, Cloudflare R2) in V2
- **Phone OTP SMS** requires Twilio/Fast2SMS API keys for production
- **Google OAuth** requires Supabase configuration

### Known Issues
- Streaming endpoints may buffer under certain reverse proxy configurations
- Memory search is keyword-based; semantic search requires embeddings
- Agent tool execution has rate limits per user per time window
- Dashboard activity limited to last 5 items per category

### Workarounds
- Use PostgreSQL for production deployments with concurrent users
- Configure `DEFAULT_LLM_PROVIDER=local` for development without API keys
- Add Twilio/Fast2SMS keys for production SMS notifications
- Configure Supabase Google OAuth for seamless sign-in

## Deployment Information

### Recommended Stack
- **Frontend**: Next.js on Netlify or Vercel
- **Backend**: FastAPI/UVicorn on Render, Railway, or Docker
- **Database**: SQLite (simple) or PostgreSQL (production)
- **AI Providers**: Google Gemini (recommended), OpenAI, or local

### Environment Variables
See `docs/RAJOS_V2_DEPLOYMENT_GUIDE.md` for complete list

### Health Checks
- `GET /health` - Must return 200 with `status: "healthy"`

### Supported Browsers
- Chrome 100+
- Firefox 100+
- Safari 15+
- Edge 100+

### Rollback Plan
1. Restore database from `docs/DATABASE_BACKUP_AND_RECOVERY.md`
2. Previous Docker image or Git commit
3. Use platform rollback features (Netlify, Vercel, Render)

## Roadmap (Post-V2)
- External vector storage (pgvector, Chroma, Pinecone)
- Multi-tenant support
- Advanced analytics dashboard
- Mobile native applications
- Plugin ecosystem for custom agents
- Enhanced automation visual builder
- Integration marketplace (Slack, Google Calendar, etc.)