from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.agent import AgentDefinitionModel
from app.schemas.agent_schema import AgentCreate, AgentUpdate

BUILTIN_AGENTS: List[Dict[str, Any]] = [
    {
        "id": "atlas",
        "name": "Atlas",
        "description": "General conversation & task orchestrator. Routes requests and coordinates across RajOS modules.",
        "system_instructions": (
            "You are Atlas, the lead general assistant and task orchestrator of RajOS personal operating system. "
            "Help the user naturally, accurately, and politely. You have access to tasks, notes, memory, knowledge search, "
            "and workspace search tools. Determine if you can answer directly or if you require a registered tool."
        ),
        "capabilities": ["conversation", "memory", "knowledge", "tasks", "notes", "search", "productivity"],
        "allowed_tools": [
            "create_task", "list_tasks", "get_task", "update_task", "complete_task", "delete_task",
            "create_note", "list_notes", "get_note", "update_note", "delete_note", "search_notes",
            "remember", "search_memory", "forget_memory", "search_knowledge", "search_workspace"
        ],
        "memory_policy": "read_write",
        "knowledge_access": "search",
        "max_steps": 5,
        "max_tool_calls": 5,
        "timeout_seconds": 30.0,
        "confirmation_policy": "default",
        "enabled": True,
        "is_builtin": True
    },
    {
        "id": "nova",
        "name": "Nova",
        "description": "Research & knowledge retrieval specialist. Searches memories, notes, and uploaded documents.",
        "system_instructions": (
            "You are Nova, the research and knowledge specialist of RajOS. "
            "Focus on retrieving grounded factual information from documents and workspace notes. "
            "Never perform destructive operations. Cite document sources clearly."
        ),
        "capabilities": ["conversation", "knowledge", "search", "notes"],
        "allowed_tools": [
            "search_knowledge", "search_workspace", "search_notes", "get_note", "list_notes"
        ],
        "memory_policy": "read",
        "knowledge_access": "full",
        "max_steps": 5,
        "max_tool_calls": 5,
        "timeout_seconds": 30.0,
        "confirmation_policy": "default",
        "enabled": True,
        "is_builtin": True
    },
    {
        "id": "sage",
        "name": "Sage",
        "description": "Planning & productivity specialist. Manages tasks, schedules, and daily habit routines.",
        "system_instructions": (
            "You are Sage, the productivity and planning specialist of RajOS. "
            "Help the user organize tasks, break down complex goals into actionable steps, schedule focused study blocks, "
            "and manage fitness & work routines."
        ),
        "capabilities": ["conversation", "tasks", "notes", "productivity"],
        "allowed_tools": [
            "create_task", "list_tasks", "get_task", "update_task", "complete_task", "delete_task",
            "create_note", "list_notes", "search_notes"
        ],
        "memory_policy": "read_write",
        "knowledge_access": "none",
        "max_steps": 5,
        "max_tool_calls": 5,
        "timeout_seconds": 30.0,
        "confirmation_policy": "default",
        "enabled": True,
        "is_builtin": True
    },
    {
        "id": "echo",
        "name": "Echo",
        "description": "Memory & context specialist. Remembers user preferences, facts, and personal context.",
        "system_instructions": (
            "You are Echo, the memory and personal context specialist of RajOS. "
            "Your main focus is managing long-term user preferences, goals, and facts using the Memory system. "
            "Search existing memories to provide personalized answers and remember explicit preferences expressed by the user."
        ),
        "capabilities": ["conversation", "memory"],
        "allowed_tools": [
            "remember", "search_memory", "forget_memory"
        ],
        "memory_policy": "read_write",
        "knowledge_access": "none",
        "max_steps": 5,
        "max_tool_calls": 5,
        "timeout_seconds": 30.0,
        "confirmation_policy": "default",
        "enabled": True,
        "is_builtin": True
    },
    {
        "id": "pulse",
        "name": "Pulse",
        "description": "Analytics & workspace telemetry monitoring specialist.",
        "system_instructions": (
            "You are Pulse, the analytics and monitoring specialist of RajOS. "
            "Analyze task completion rates, notes count, system status, and provide summary insights to the user."
        ),
        "capabilities": ["conversation", "search", "productivity"],
        "allowed_tools": [
            "search_workspace", "list_tasks", "list_notes"
        ],
        "memory_policy": "read",
        "knowledge_access": "none",
        "max_steps": 5,
        "max_tool_calls": 5,
        "timeout_seconds": 30.0,
        "confirmation_policy": "default",
        "enabled": True,
        "is_builtin": True
    }
]


class AgentRegistry:

    def seed_builtin_agents(self, db: Session) -> None:
        """Seeds or updates built-in agents in DB to ensure table synchronization."""
        for b_data in BUILTIN_AGENTS:
            existing = db.query(AgentDefinitionModel).filter(AgentDefinitionModel.id == b_data["id"]).first()
            if not existing:
                agent = AgentDefinitionModel(
                    id=b_data["id"],
                    name=b_data["name"],
                    description=b_data["description"],
                    system_instructions=b_data["system_instructions"],
                    capabilities=b_data["capabilities"],
                    allowed_tools=b_data["allowed_tools"],
                    memory_policy=b_data["memory_policy"],
                    knowledge_access=b_data["knowledge_access"],
                    max_steps=b_data["max_steps"],
                    max_tool_calls=b_data["max_tool_calls"],
                    timeout_seconds=b_data["timeout_seconds"],
                    confirmation_policy=b_data["confirmation_policy"],
                    enabled=b_data["enabled"],
                    is_builtin=True,
                    user_id=None
                )
                db.add(agent)
        db.commit()

    def get_agent(self, db: Session, agent_id: str, user_id: Optional[int] = None) -> Optional[AgentDefinitionModel]:
        """Resolves agent by ID. Checks for global built-in or user custom agent."""
        self.seed_builtin_agents(db)
        query = db.query(AgentDefinitionModel).filter(AgentDefinitionModel.id == agent_id.lower())
        if user_id is not None:
            query = query.filter(
                (AgentDefinitionModel.is_builtin == True) | (AgentDefinitionModel.user_id == user_id)
            )
        return query.first()

    def list_agents(self, db: Session, user_id: Optional[int] = None, include_disabled: bool = False) -> List[AgentDefinitionModel]:
        """Lists all agents available to user (built-in + custom)."""
        self.seed_builtin_agents(db)
        query = db.query(AgentDefinitionModel)
        if user_id is not None:
            query = query.filter(
                (AgentDefinitionModel.is_builtin == True) | (AgentDefinitionModel.user_id == user_id)
            )
        if not include_disabled:
            query = query.filter(AgentDefinitionModel.enabled == True)
        return query.order_by(AgentDefinitionModel.is_builtin.desc(), AgentDefinitionModel.name.asc()).all()

    def register_custom_agent(self, db: Session, user_id: int, payload: AgentCreate) -> AgentDefinitionModel:
        """Creates a custom user agent with backend validation."""
        self.seed_builtin_agents(db)
        agent_id = (payload.id or f"custom_{payload.name.lower().replace(' ', '_')}").strip().lower()

        # Prevent overriding built-in agents
        if db.query(AgentDefinitionModel).filter(AgentDefinitionModel.id == agent_id).first():
            raise ValueError(f"Agent ID '{agent_id}' already exists.")

        agent = AgentDefinitionModel(
            id=agent_id,
            name=payload.name,
            description=payload.description,
            system_instructions=payload.system_instructions,
            capabilities=payload.capabilities,
            allowed_tools=payload.allowed_tools,
            memory_policy=payload.memory_policy,
            knowledge_access=payload.knowledge_access,
            max_steps=payload.max_steps,
            max_tool_calls=payload.max_tool_calls,
            timeout_seconds=payload.timeout_seconds,
            confirmation_policy=payload.confirmation_policy,
            enabled=payload.enabled,
            is_builtin=False,
            user_id=user_id
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def update_agent(self, db: Session, agent_id: str, user_id: int, payload: AgentUpdate) -> Optional[AgentDefinitionModel]:
        """Updates custom agent definitions. Built-in agents instructions cannot be modified by regular users."""
        agent = self.get_agent(db, agent_id, user_id)
        if not agent:
            return None
        if agent.is_builtin and user_id != 1:  # Allow admin user 1 or lock built-in
            raise ValueError("Built-in system agents cannot be modified.")

        update_dict = payload.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(agent, key, value)

        db.commit()
        db.refresh(agent)
        return agent

    def delete_custom_agent(self, db: Session, agent_id: str, user_id: int) -> bool:
        """Deletes a custom user agent."""
        agent = db.query(AgentDefinitionModel).filter(
            AgentDefinitionModel.id == agent_id.lower(),
            AgentDefinitionModel.user_id == user_id,
            AgentDefinitionModel.is_builtin == False
        ).first()

        if not agent:
            return False

        db.delete(agent)
        db.commit()
        return True


agent_registry = AgentRegistry()
