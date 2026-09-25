# RajOS V2 — AI Agent System 2.0 System Documentation

## 1. Overview & Architecture

RajOS V2 Phase 7 introduces a controlled, safe AI Agent System where specialized agents orchestrate existing RajOS subsystems (AI Core, Conversation, Memory 2.0, Knowledge & RAG 2.0, Tool Registry 2.0).

```text
                    ┌──────────────────┐
                    │   RajOS Frontend │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Conversation   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Agent Service  │
                    └────────┬─────────┘
                             │
                 ┌───────────┼───────────┐
                 ▼           ▼           ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐
          │ Context  │ │ AI Core  │ │ Policies │
          │ Builder  │ │          │ │/Limits   │
          └────┬─────┘ └────┬─────┘ └──────────┘
               │            │
        ┌──────┼──────┐     │
        ▼      ▼      ▼     ▼
     Memory   RAG  Conversation
        │      │      │
        └──────┼──────┘
               │
               ▼
        ┌──────────────┐
        │ Tool Registry│
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Tool Services│
        └──────┬───────┘
               │
               ▼
           RajOS DB
```

---

## 2. Agent Definition Schema (`AgentDefinitionModel`)

Every agent definition specifies:
- `id`: String primary key (e.g. `"atlas"`, `"nova"`, `"sage"`, `"echo"`, `"pulse"`, `"custom_reviewer"`).
- `name`: Human-readable name.
- `description`: Agent specialization summary.
- `system_instructions`: Base system prompt / persona instructions.
- `capabilities`: Explicit capability permissions (`conversation`, `memory`, `knowledge`, `tasks`, `notes`, `search`, `productivity`).
- `allowed_tools`: Explicit whitelist of registered tools this agent is permitted to execute.
- `memory_policy`: `"none"`, `"read"`, `"read_write"`.
- `knowledge_access`: `"none"`, `"search"`, `"full"`.
- `max_steps`: Hard step limit per execution run (default 5).
- `max_tool_calls`: Hard tool call limit per execution run (default 5).
- `timeout_seconds`: Execution timeout boundary (default 30s).
- `confirmation_policy`: `"default"`, `"always"`, `"never"`.
- `enabled`: Boolean flag enabling/disabling the agent.
- `is_builtin`: Boolean flag distinguishing core system agents.
- `user_id`: Ownership reference for custom user agents.

---

## 3. Pre-Seeded Built-In Agents

1. **Atlas** (General Conversation & Task Orchestrator)
   - Capabilities: `["conversation", "memory", "knowledge", "tasks", "notes", "search", "productivity"]`
   - Memory Policy: `read_write` | Knowledge Access: `search`
2. **Nova** (Research & Knowledge Specialist)
   - Capabilities: `["conversation", "knowledge", "search", "notes"]`
   - Allowed Tools: `["search_knowledge", "search_workspace", "search_notes", "get_note", "list_notes"]`
   - Memory Policy: `read` | Knowledge Access: `full`
3. **Sage** (Productivity & Task Specialist)
   - Capabilities: `["conversation", "tasks", "notes", "productivity"]`
   - Allowed Tools: `["create_task", "list_tasks", "get_task", "update_task", "complete_task", "delete_task", "create_note", "list_notes", "search_notes"]`
   - Memory Policy: `read_write` | Knowledge Access: `none`
4. **Echo** (Memory & Context Specialist)
   - Capabilities: `["conversation", "memory"]`
   - Allowed Tools: `["remember", "search_memory", "forget_memory"]`
   - Memory Policy: `read_write` | Knowledge Access: `none`
5. **Pulse** (Analytics & Diagnostics Specialist)
   - Capabilities: `["conversation", "search", "productivity"]`
   - Allowed Tools: `["search_workspace", "list_tasks", "list_notes"]`
   - Memory Policy: `read` | Knowledge Access: `none`

---

## 4. Execution Loop & Safeguards

The `AgentService` orchestrates execution loop rounds:
1. **Context Assembly**: `AgentContextBuilder` formats persona instructions, scoped memory context, scoped RAG knowledge context, and allowed tool JSON schemas.
2. **AI Decision**: Model outputs either a final text response or a JSON tool request (`{"tool_call": {"name": "...", "arguments": {...}}}`).
3. **Capability Validation**: Validates requested tool against `agent.allowed_tools`.
4. **Controlled Execution**: Passes tool call to `ToolExecutor` (validating permissions, Pydantic arguments, and confirmation policies).
5. **Loop Capping**: Stops execution if step count exceeds `max_steps`, tool calls exceed `max_tool_calls`, runtime exceeds `timeout_seconds`, or repeated tool calls are detected (`limit_reached`).
6. **State Tracking**: Records run state in `agent_runs` table (`run_id`, `status`, `current_step`, `step_history`, `final_response`).

---

## 5. Security & Isolation Controls

- **No Code Execution**: Arbitrary Python, shell commands, or raw SQL queries are strictly prohibited.
- **Strict User Scoping**: `user_id` is derived from authenticated JWT session context. Custom agents and agent runs are isolated per user.
- **Confirmation Integration**: Destructive actions pass through Phase 6 confirmation token flow before execution.
- **Prompt Injection Defense**: Tool outputs in agent context are tagged with `<UNTRUSTED_TOOL_RESULT tool="...">`.

---

## 6. API Endpoints

- `GET /agents`: List available agents for user.
- `GET /agents/{agent_id}`: Get single agent details.
- `POST /agents`: Create custom user agent.
- `PUT /agents/{agent_id}`: Update custom agent definition.
- `DELETE /agents/{agent_id}`: Delete custom agent.
- `POST /agents/{agent_id}/run`: Execute agent run.
- `GET /agents/runs/{run_id}`: Get run status & step history.
- `POST /agents/runs/{run_id}/cancel`: Cancel active run.
