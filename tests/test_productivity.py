import pytest
from datetime import datetime, timedelta
from app.models.task import Task
from app.models.user import User
from app.productivity.priority_engine import priority_engine
from app.productivity.task_analyzer import task_analyzer
from app.productivity.workload_service import workload_service
from app.productivity.recommendation_engine import recommendation_engine
from app.productivity.planning_service import planning_service
from app.tools.tool_registry import tool_registry
from app.tools.tool_context import ToolExecutionContext


def test_priority_engine_scoring(db_session, test_user):
    now = datetime.utcnow()
    # High priority overdue task with subtasks
    t1 = Task(
        title="High Overdue Task",
        priority="high",
        due_date=now - timedelta(days=2),
        user_id=test_user.id
    )
    db_session.add(t1)
    db_session.commit()
    db_session.refresh(t1)

    analysis = priority_engine.analyze_priority(t1, subtasks_count=2)
    assert analysis["computed_priority"] in ["urgent", "high"]
    assert analysis["priority_score"] >= 80
    assert len(analysis["reasons"]) > 0
    assert any("Overdue" in r for r in analysis["reasons"])


def test_task_analyzer_categories(db_session, test_user):
    now = datetime.utcnow()

    # Create various tasks
    t_overdue = Task(title="Overdue Homework", priority="high", due_date=now - timedelta(days=1), user_id=test_user.id)
    t_soon = Task(title="Due Soon Exam", priority="normal", due_date=now + timedelta(days=2), user_id=test_user.id)
    t_quick = Task(title="Quick Email", estimated_duration=15, user_id=test_user.id)
    t_heavy = Task(title="Heavy Project", estimated_duration=180, user_id=test_user.id)
    t_unscheduled = Task(title="Unscheduled High Priority", priority="high", due_date=None, user_id=test_user.id)

    db_session.add_all([t_overdue, t_soon, t_quick, t_heavy, t_unscheduled])
    db_session.commit()

    analysis = task_analyzer.analyze_user_tasks(db_session, test_user.id)

    assert len(analysis["overdue_tasks"]) == 1
    assert analysis["overdue_tasks"][0]["title"] == "Overdue Homework"
    assert len(analysis["due_soon_tasks"]) == 1
    assert len(analysis["quick_wins"]) >= 1
    assert len(analysis["heavy_tasks"]) == 1
    assert len(analysis["unscheduled_tasks"]) >= 1


def test_workload_service_daily_brief(db_session, test_user):
    now = datetime.utcnow()
    t1 = Task(title="Task Today", due_date=now, priority="high", estimated_duration=60, user_id=test_user.id)
    db_session.add(t1)
    db_session.commit()

    brief = workload_service.get_daily_brief(db_session, test_user.id)

    assert brief["date"] == now.strftime("%Y-%m-%d")
    assert "overdue_count" in brief
    assert "due_today_count" in brief
    assert "recommended_focus" in brief


def test_workload_service_weekly_summary_and_trends(db_session, test_user):
    now = datetime.utcnow()
    t1 = Task(title="Done Task 1", completed=True, completed_at=now - timedelta(days=1), created_at=now - timedelta(days=2), user_id=test_user.id)
    t2 = Task(title="Done Task 2", completed=True, completed_at=now - timedelta(days=3), created_at=now - timedelta(days=4), user_id=test_user.id)
    t3 = Task(title="Pending Task 3", completed=False, created_at=now - timedelta(days=5), user_id=test_user.id)

    db_session.add_all([t1, t2, t3])
    db_session.commit()

    summary = workload_service.get_weekly_summary(db_session, test_user.id)
    assert summary["tasks_completed"] == 2
    assert summary["tasks_created"] == 3

    trends = workload_service.get_productivity_trends(db_session, test_user.id)
    assert trends["has_sufficient_data"] is True
    assert len(trends["daily_data"]) == 7


def test_recommendations_generation(db_session, test_user):
    now = datetime.utcnow()
    t1 = Task(title="Overdue Critical Project", priority="high", due_date=now - timedelta(days=3), user_id=test_user.id)
    db_session.add(t1)
    db_session.commit()

    recs = recommendation_engine.generate_recommendations(db_session, test_user.id)

    assert len(recs) >= 1
    assert recs[0]["type"] == "overdue_task"
    assert recs[0]["priority"] == "urgent"
    assert "reason" in recs[0]


def test_planning_service_plan_day_and_breakdown(db_session, test_user):
    t1 = Task(title="Study Computer Networks", priority="high", estimated_duration=90, user_id=test_user.id)
    t2 = Task(title="Build RajOS Frontend", priority="normal", estimated_duration=120, user_id=test_user.id)
    db_session.add_all([t1, t2])
    db_session.commit()

    plan = planning_service.plan_day(db_session, test_user.id, available_minutes=300)
    assert len(plan["schedule"]) == 2
    assert plan["allocated_minutes"] == 210

    breakdown = planning_service.breakdown_task(title="Build RajOS College Project")
    assert breakdown["total_subtasks"] >= 3
    assert breakdown["total_estimated_duration"] > 0


def test_productivity_tool_registry_execution(db_session, test_user):
    context = ToolExecutionContext(user_id=test_user.id, permissions=["tasks.read", "tasks.write"])

    tool_daily = tool_registry.get_tool("get_daily_brief")
    assert tool_daily is not None
    res_daily = tool_daily.execute({}, context)
    assert "recommended_focus" in res_daily

    tool_plan = tool_registry.get_tool("plan_tasks")
    assert tool_plan is not None
    res_plan = tool_plan.execute({"available_minutes": 240}, context)
    assert "schedule" in res_plan


def test_user_data_isolation_productivity(db_session, test_user):
    user_b = User(username="user_b", email="user_b@example.com", hashed_password="pw")
    db_session.add(user_b)
    db_session.commit()
    db_session.refresh(user_b)

    # Task for test_user
    t_user_a = Task(title="Private User A Task", user_id=test_user.id)
    # Task for user_b
    t_user_b = Task(title="Private User B Task", user_id=user_b.id)

    db_session.add_all([t_user_a, t_user_b])
    db_session.commit()

    # User A analysis
    res_a = task_analyzer.analyze_user_tasks(db_session, test_user.id)
    titles_a = [t["title"] for t in res_a["quick_wins"] + res_a["unscheduled_tasks"] + res_a["overdue_tasks"] + res_a["high_impact_tasks"]]

    assert "Private User A Task" in titles_a or res_a["total_tasks"] == 1
    assert "Private User B Task" not in titles_a
