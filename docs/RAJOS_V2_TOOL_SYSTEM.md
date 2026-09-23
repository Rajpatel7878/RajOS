# RajOS V2 — Tool Registry & Function Calling 2.0 System Documentation

## 1. Overview & Architecture

RajOS V2 Phase 6 transforms RajOS from a passive response generator into a secure, controlled AI operating system capable of executing actions safely through registered tools.

```text
                         USER
                           │
                           ↓
                  ┌─────────────────┐
                  │ Conversation    │
                  │ Intelligence    │
                  └────────┬────────┘
                           ↓
                    ┌──────────────┐
                    │   AI Core    │
                    └──────┬───────┘
                           ↓
                    Tool Required?
                       /       \
                     NO         YES
                     │           │
                     │      ┌──────────────┐
                     │      │Tool Registry │
                     │      └──────┬───────┘
                     │             ↓
                     │      Permission Check
                     │             ↓
                     │      Argument Validation
                     │             ↓
                     │       Confirmation?
                     │          /      \
                     │        YES       NO
                     │         ↓         ↓
                     │      USER      Executor
                     │       ↓           ↓
                     │    Confirm      Service
                     │                   ↓
                     │                Database
                     │                   ↓
                     │              Tool Result
                     │                   ↓
                     └─────────────→ AI Core
                                     ↓
                                  Response
```

---

## 2. Security Principles

1. **No Arbitrary Code Execution**: The LLM is untrusted code. It can NEVER directly execute Python code, shell commands, raw SQL queries (`execute_sql`), or make un-sanitized filesystem or network requests.
2. **User Context Scoping**: `user_id` is ALWAYS extracted from the authenticated JWT token / request context. LLM argument injection cannot bypass or manipulate ownership.
3. **Confirmation Policy**: Destructive actions (e.g. `delete_task`, `delete_note`, `forget_memory`) require explicit user confirmation via the frontend UI before execution.
4. **Prompt Injection Defense**: Output data returned by tools is wrapped in `<UNTRUSTED_TOOL_RESULT tool="...">` tags to prevent data payloads from hijacking system instructions.

---

## 3. Tool Definition & Registry

Every tool inherits from `ToolDefinition` and defines:
- `name`: Machine-readable unique tool name.
- `description`: Detailed description explaining when and when NOT to use the tool.
- `category`: `tasks`, `notes`, `memory`, `knowledge`, `search`, `productivity`, `system`.
- `read_only`: Boolean flag indicating whether data is modified.
- `risk_level`: `low`, `medium`, `high`.
- `requires_confirmation`: Boolean flag for destructive operations.
- `required_permissions`: List of permission strings (e.g. `["tasks.write"]`).
- `args_model`: Pydantic model enforcing strict type checking, validation, and constraints.

### Registry Interface (`ToolRegistry`)
- `register(tool)`: Register tool definition.
- `unregister(name)`: Unregister tool definition.
- `get_tool(name)`: Retrieve registered tool.
- `list_tools(category, permissions)`: Filter tools based on user permissions.
- `export_llm_schemas(permissions)`: Convert available tools to OpenAI/Gemini compatible function call JSON schemas.

---

## 4. Tool Executor (`ToolExecutor`)

The `ToolExecutor` coordinates execution:
1. **Tool Resolution**: Resolves tool by name from `ToolRegistry`.
2. **Availability Check**: Verifies tool is enabled.
3. **Permission Check**: Ensures authenticated user possesses required permissions.
4. **Security Filter**: Scans JSON argument payloads for SQL or shell injection attempts.
5. **Argument Validation**: Validates arguments against Pydantic schema model.
6. **Confirmation Verification**: Pauses execution if `requires_confirmation=True` and no explicit confirmation token is present.
7. **Safe Execution & Capping**: Executes tool, records execution time, and truncates outputs exceeding size caps (10,000 chars) to prevent context exhaustion.

---

## 5. Starter Tool Suite

| Category | Tool Name | Description | Read-Only | Confirmation |
|---|---|---|---|---|
| **Tasks** | `create_task` | Create a new task | ❌ | ❌ |
| **Tasks** | `list_tasks` | List user's tasks |  | ❌ |
| **Tasks** | `get_task` | Get task details by ID |  | ❌ |
| **Tasks** | `update_task` | Update an existing task | ❌ | ❌ |
| **Tasks** | `complete_task` | Mark task completed | ❌ | ❌ |
| **Tasks** | `delete_task` | Delete task by ID | ❌ |  |
| **Notes** | `create_note` | Create a new note | ❌ | ❌ |
| **Notes** | `list_notes` | List user's notes |  | ❌ |
| **Notes** | `get_note` | Get note content by ID |  | ❌ |
| **Notes** | `update_note` | Update note title/content | ❌ | ❌ |
| **Notes** | `delete_note` | Delete note by ID | ❌ |  |
| **Notes** | `search_notes` | Keyword search in notes |  | ❌ |
| **Memory** | `remember` | Store long-term memory | ❌ | ❌ |
| **Memory** | `search_memory` | Search long-term memory |  | ❌ |
| **Memory** | `forget_memory` | Delete long-term memory | ❌ |  |
| **Knowledge**| `search_knowledge`| Search indexed RAG documents |  | ❌ |
| **Search** | `search_workspace`| Multi-entity workspace search |  | ❌ |

---

## 6. API Contracts

### REST Endpoints
- `POST /chat/message`: Main chat interaction endpoint. Supports tool execution loop (`MAX_TOOL_CALL_ROUNDS = 5`) and returns `requires_confirmation` and `tool_executions` metadata.
- `GET /api/v1/tools`: Capability discovery endpoint returning available tool schemas for the authenticated user.
