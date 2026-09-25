from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.database.connection import Base


class AgentDefinitionModel(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    system_instructions = Column(Text, nullable=False)
    capabilities = Column(JSON, default=list, nullable=False)  # e.g. ["conversation", "memory", "knowledge", "tasks"]
    allowed_tools = Column(JSON, default=list, nullable=False)  # e.g. ["create_task", "search_knowledge"]
    memory_policy = Column(String, default="read_write")  # "none", "read", "read_write"
    knowledge_access = Column(String, default="search")  # "none", "search", "full"
    max_steps = Column(Integer, default=5)
    max_tool_calls = Column(Integer, default=5)
    timeout_seconds = Column(Float, default=30.0)
    confirmation_policy = Column(String, default="default")
    enabled = Column(Boolean, default=True)
    is_builtin = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for global built-in agents

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="custom_agents", foreign_keys=[user_id])


class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # "pending", "running", "waiting_for_confirmation", "completed", "failed", "cancelled", "timeout", "limit_reached"
    current_step = Column(Integer, default=0)
    step_history = Column(JSON, default=list, nullable=False)
    final_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    confirmation_token = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="agent_runs", foreign_keys=[user_id])
    agent = relationship("AgentDefinitionModel", backref="runs", foreign_keys=[agent_id])
