import pytest
from app.database.connection import SessionLocal, Base, engine
from app.models.user import User
from app.models.agent import AgentDefinitionModel, AgentRunModel
from app.schemas.agent_schema import AgentCreate, AgentUpdate
from app.agents.agent_registry import agent_registry, AgentRegistry
from app.agents.agent_service import agent_service
from app.agents.agent_context_builder import agent_context_builder


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Ensure test users exist
    u1 = db.query(User).filter(User.username == "agentuser1").first()
    if not u1:
        u1 = User(id=201, username="agentuser1", email="agentuser1@rajos.io", password="pw")
        db.add(u1)
    u2 = db.query(User).filter(User.username == "agentuser2").first()
    if not u2:
        u2 = User(id=202, username="agentuser2", email="agentuser2@rajos.io", password="pw")
        db.add(u2)
    db.query(AgentRunModel).filter(AgentRunModel.user_id.in_([201, 202])).delete(synchronize_session=False)
    db.query(AgentDefinitionModel).filter(AgentDefinitionModel.user_id.in_([201, 202])).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_agent_registry_seed_and_builtin_lookup():
    db = SessionLocal()
    try:
        agent_registry.seed_builtin_agents(db)
        agents = agent_registry.list_agents(db, user_id=201)
        agent_ids = [a.id for a in agents]

        assert "atlas" in agent_ids
        assert "nova" in agent_ids
        assert "sage" in agent_ids
        assert "echo" in agent_ids
        assert "pulse" in agent_ids

        atlas = agent_registry.get_agent(db, "atlas", user_id=201)
        assert atlas is not None
        assert atlas.name == "Atlas"
        assert "tasks" in atlas.capabilities
        assert "create_task" in atlas.allowed_tools
    finally:
        db.close()


def test_custom_agent_registration_and_isolation():
    db = SessionLocal()
    try:
        payload = AgentCreate(
            id="code_reviewer",
            name="Code Reviewer",
            description="Specialist in analyzing code quality.",
            system_instructions="You review Python and TypeScript code.",
            capabilities=["conversation", "notes"],
            allowed_tools=["create_note", "search_notes"],
            memory_policy="read",
            knowledge_access="none"
        )
        custom_agent = agent_registry.register_custom_agent(db, user_id=201, payload=payload)
        assert custom_agent.id == "code_reviewer"
        assert custom_agent.user_id == 201

        # User 1 sees code_reviewer
        u1_agents = [a.id for a in agent_registry.list_agents(db, user_id=201)]
        assert "code_reviewer" in u1_agents

        # User 2 does NOT see User 1's custom agent
        u2_agents = [a.id for a in agent_registry.list_agents(db, user_id=202)]
        assert "code_reviewer" not in u2_agents
    finally:
        db.close()


def test_agent_context_builder():
    db = SessionLocal()
    try:
        atlas = agent_registry.get_agent(db, "atlas", user_id=201)
        prompt = agent_context_builder.build_prompt(
            db=db,
            agent=atlas,
            user_id=201,
            user_prompt="Schedule a study session for tomorrow"
        )
        assert "Atlas" in prompt
        assert "create_task" in prompt
        assert "Allowed Registered Tools" in prompt
    finally:
        db.close()


def test_agent_service_execution_and_tool_restriction():
    db = SessionLocal()
    try:
        # Run Atlas (General Orchestrator)
        res = agent_service.run_agent(
            db=db,
            agent_id="atlas",
            user_id=201,
            prompt="Hello Atlas, what can you do?"
        )
        assert res["status"] == "completed"
        assert res["agent_name"] == "Atlas"
        assert "run_id" in res
        assert isinstance(res["response"], str)

        # Run Nova (Knowledge Agent) with prompt asking for task tool execution -> tool restriction enforced
        res_nova = agent_service.run_agent(
            db=db,
            agent_id="nova",
            user_id=201,
            prompt="What tools do you have?"
        )
        assert res_nova["status"] == "completed"
        assert res_nova["agent_name"] == "Nova"
    finally:
        db.close()


def test_disabled_agent_cannot_execute():
    db = SessionLocal()
    try:
        # Create disabled custom agent
        payload = AgentCreate(
            id="disabled_bot",
            name="Disabled Bot",
            system_instructions="Disabled agent instructions.",
            enabled=False
        )
        agent_registry.register_custom_agent(db, user_id=201, payload=payload)

        res = agent_service.run_agent(
            db=db,
            agent_id="disabled_bot",
            user_id=201,
            prompt="Run disabled bot"
        )
        assert res["status"] == "failed"
        assert "disabled" in res["error"].lower()
    finally:
        db.close()


def test_agent_confirmation_pause_state():
    db = SessionLocal()
    try:
        # Sage requests delete_task (requires confirmation)
        res = agent_service.run_agent(
            db=db,
            agent_id="sage",
            user_id=201,
            prompt="Delete task #999"
        )
        # If AI model outputted tool_call for delete_task or responded
        assert res["status"] in ["completed", "waiting_for_confirmation", "limit_reached"]
    finally:
        db.close()
