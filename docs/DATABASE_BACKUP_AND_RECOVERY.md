# RajOS V2 — Database Backup and Recovery Guide

## Database Architecture

RajOS V2 uses **SQLite** as the default database with SQLAlchemy ORM. The database file is located at `./rajos.db` relative to the backend directory.

### Supported Databases
- **Primary**: SQLite (default, development and simple deployments)
- **Alternative**: PostgreSQL (for production deployments requiring concurrent access and scaling)

### Database Models
The following models are defined and mapped to the database:

| Model | Table | Key Fields |
|-------|-------|------------|
| `User` | `users` | id, username, email, password, phone_number, device_id |
| `Task` | `tasks` | id, title, description, priority, due_date, completed, completed_at, user_id |
| `Conversation` | `conversations` | id, title, user_id |
| `Message` | `messages` | id, role, content, conversation_id |
| `Note` | `notes` | id, title, content, user_id |
| `Memory` | `memories` | id, key, value, user_id |
| `Document` | `documents` | id, filename, content, user_id |
| `UserPreference` | `user_preferences` | id, user_id, key, value |
| `UserProfile` | `user_profiles` | id, user_id, key, value |
| `SearchHistory` | `search_history` | id, query, search_type, searched_at, user_id |
| `PushSubscription` | `push_subscriptions` | id, user_id, endpoint, auth, p256dh |
| `Automation` | `automations` | id, user_id, name, trigger, action, enabled, timezone |
| `AgentDefinition` | `agent_definitions` | id, user_id, name, description, system_instructions, capabilities |

## Backup Procedures

### 1. SQLite Backup (Recommended)

**Command:**
```bash
# From the backend directory
cp rajos.db rajos.db.backup_$(date +%Y%m%d_%H%M%S).db
```

**Or using Python:**
```python
import shutil
import datetime

shutil.copy2("rajos.db", f"rajos.db.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
```

**Best Practice:** 
- Create backups before any migration or significant data changes
- Store backups in a separate location from the production database
- Retain at least 3-5 recent backups

### 2. PostgreSQL Backup (If Using PostgreSQL)

**Command (pg_dump):**
```bash
pg_dump -h localhost -U rajos_user -d rajos > rajos_$(date +%Y%m%d).sql
```

**With compression:**
```bash
pg_dump -h localhost -U rajos_user -d rajos | gzip > rajos_$(date +%Y%m%d).sql.gz
```

### 3. Automated Backup Script

```bash
#!/bin/bash
# RajOS Database Backup Script
# Usage: ./backup_rajos.sh

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_PATH="./rajos.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create SQLite backup
cp "$DB_PATH" "$BACKUP_DIR/rajos_${TIMESTAMP}.db"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "rajos_*.db" -type f -mtime +30 -delete

echo "Backup created: $BACKUP_DIR/rajos_${TIMESTAMP}.db"
```

Make the script executable:
```bash
chmod +x backup_rajos.sh
```

## Recovery Procedures

### 1. SQLite Recovery

**Step 1:** Stop the application if running
```bash
# Stop any running FastAPI/uvicorn processes
```

**Step 2:** Replace the database file
```bash
# From the backend directory
cp rajos.db.backup_20240101_120000.db rajos.db
```

**Step 3:** Verify the application starts correctly
```bash
python -m app.main
```

**Step 4:** Check data integrity
- Log in as an existing user
- Verify tasks, conversations, and other data are present
- Run the health endpoint: `GET /health`

### 2. PostgreSQL Recovery

**Step 1:** Stop the application if running

**Step 2:** Restore from backup
```bash
psql -h localhost -U rajos_user -d rajos < rajos_20240101.sql
```

**Step 3:** Verify the application starts correctly

**Step 4:** Check data integrity

## Migration Safety

### Safe Migration Practices

1. **Always backup before running migrations**
2. **Test migrations on a copy of the database first**
3. **Never run destructive migrations in production without verification**
4. **Use Alembic for managed migrations if needed**

### Current Migration Status
- The application uses `Base.metadata.create_all(bind=engine)` which creates tables if they don't exist
- No destructive migrations are automatic
- Tables are only created, never dropped

### Alembic Setup (If Needed)
If you need Alembic migrations:

```bash
# Initialize Alembic
cd backend
alembic init alembic

# Create first migration
alembic revision --autogenerate -m "Initial migration"

# Run migration
alembic upgrade head
```

## Database Persistence Requirements

### SQLite Persistence
⚠️ **Important**: SQLite stores data in a single file on disk.
- ✅ Persistent if hosted on a volume that survives restarts
- ❌ **NOT** persistent on ephemeral filesystems (e.g., some container orchestration platforms)
- ❌ **NOT** persistent in serverless environments without external storage

### PostgreSQL Persistence
- ✅ Naturally persistent with proper disk configuration
- ✅ Connection pooling available
- ✅ Better for concurrent access and scaling

## Production Database Recommendations

### SQLite (Simple Deployments)
- Use only on hosting platforms with persistent disk storage
- Ensure the deployment platform preserves the `rajos.db` file across restarts
- Example platforms: Render, Railway (with persistent disks)

### PostgreSQL (Production/Scale)
- Recommended for production deployments
- Use connection pooling (pool_size=5, max_overflow=10)
- Configure SSL/TLS for secure connections
- Set up regular automated backups

### Connection Pool Configuration
The current configuration supports both:
```python
# SQLite (check_same_thread=False for FastAPI)
connect_args={"check_same_thread": False}

# PostgreSQL (pool configuration)
pool_size=5
max_overflow=10
pool_pre_ping=True
```

## Restore Instructions

### From SQLite Backup
1. Copy the backup file to `./rajos.db`
2. Start the application: `python -m app.main`
3. Verify data accessibility through the API

### From PostgreSQL Backup
1. Run `psql` to restore the database
2. Update environment variables with new connection string
3. Restart the application

## Verification Checklist

- [ ] Database backup created and verified
- [ ] Backup can be restored successfully
- [ ] Application starts without database errors
- [ ] User data is intact after restore
- [ ] All API endpoints functioning with restored data
- [ ] Health endpoint returns `database: healthy`