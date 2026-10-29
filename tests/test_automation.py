"""Tests — Phase 9: Automation Engine 2.0.

Covers:
  - Model creation (Automation + AutomationRun)
  - Trigger engine: schedule, interval, onetime, event matching
  - Condition engine: field evaluation, operators, vacuous truth
  - Execution engine: conditions gate, action success/failure, failure_policy
  - Automation service: CRUD, enable/disable, preview, fire_event
  - API endpoints: create, list, get, update, delete, enable, disable, run, runs
"""

import itertools as _itertools

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.automation.automation_models import Automation, AutomationRun
from app.automation.trigger_engine import TriggerEngine
from app.automation.condition_engine import ConditionEngine
from app.automation.execution_engine import ExecutionEngine
from app.automation.automation_service import AutomationService
from app.automation.automation_schemas import (
    AutomationCreate,
    AutomationUpdate,
    TriggerConfig,
    ActionStep,
    ConditionRule,
)


# ──────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _reset_execution_engine_state():
    """Clear the engine's process-local guards between tests.

    Automation ids are reused across tests (each test rolls back), so rate
    limit windows, active-run markers and cancel flags from one test must not
    leak into the next one.
    """
    from app.automation import execution_engine as ee

    def _clear():
        ee._RUN_TIMESTAMPS.clear()
        ee._ACTIVE_RUNS.clear()
        ee._CANCEL_REQUESTED.clear()

    _clear()
    yield
    _clear()


def _app_session():
    """A session on the shared application database (see tests/conftest.py).

    Objects that the scheduler, tools and background threads touch live here
    rather than in the per-test in-memory database.
    """
    from app.database.connection import SessionLocal

    return SessionLocal()


_UNIQUE_USER_SEQ = _itertools.count(9_100_000)


def _unique_user_id() -> int:
    """A user id nobody else in the suite will collide with."""
    return next(_UNIQUE_USER_SEQ)


def _app_user(db: Session, notifications_enabled: bool = False):
    """Create a uniquely-named user on the application database."""
    from uuid import uuid4

    from app.models.user import User

    suffix = uuid4().hex[:10]
    user = User(
        username=f"autotest_{suffix}",
        email=f"autotest_{suffix}@rajos.io",
        password="TestPassword123!",
        notifications_enabled=notifications_enabled,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_automation(db: Session, user_id: int, **kwargs) -> Automation:
    # The execution engine re-checks that the owner exists on every run.
    from app.models.user import User

    if db.get(User, user_id) is None:
        db.add(User(
            id=user_id,
            username=f"automation_user_{user_id}",
            email=f"automation_user_{user_id}@rajos.io",
            password="pw",
            notifications_enabled=True,
        ))
        db.commit()

    defaults = dict(
        user_id=user_id,
        name="Test Automation",
        trigger_type="schedule",
        trigger_config={"time": "08:00"},
        conditions=[],
        actions=[],
        timezone="Asia/Kolkata",
        failure_policy="stop",
        enabled=True,
    )
    defaults.update(kwargs)
    a = Automation(**defaults)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ──────────────────────────────────────────────────────────────
# 1. Trigger Engine
# ──────────────────────────────────────────────────────────────

class TestTriggerEngine:

    def setup_method(self):
        self.engine = TriggerEngine()

    def test_schedule_daily_returns_future(self):
        now = datetime.now(timezone.utc)
        cfg = {"time": "08:00"}
        result = self.engine.compute_next_run("schedule", cfg, after=now)
        assert result is not None
        assert result > now

    def test_schedule_specific_days(self):
        now = datetime.now(timezone.utc)
        cfg = {"time": "09:00", "days": ["mon", "tue", "wed", "thu", "fri"]}
        result = self.engine.compute_next_run("schedule", cfg, after=now)
        assert result is not None
        assert result > now
        day_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        assert day_map[result.weekday()] in cfg["days"]

    def test_interval_returns_correct_future(self):
        now = datetime.now(timezone.utc)
        cfg = {"interval_minutes": 30}
        result = self.engine.compute_next_run("interval", cfg, after=now)
        assert result is not None
        diff = (result - now).total_seconds()
        assert 29 * 60 <= diff <= 31 * 60

    def test_onetime_future(self):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        cfg = {"run_at": future}
        now = datetime.now(timezone.utc)
        result = self.engine.compute_next_run("onetime", cfg, after=now)
        assert result is not None
        assert result > now

    def test_onetime_past_returns_none(self):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        cfg = {"run_at": past}
        now = datetime.now(timezone.utc)
        result = self.engine.compute_next_run("onetime", cfg, after=now)
        assert result is None

    def test_event_trigger_returns_none(self):
        result = self.engine.compute_next_run("event", {"event_type": "task.completed"})
        assert result is None

    def test_event_matches_correctly(self):
        cfg = {"event_type": "task.completed"}
        assert self.engine.matches_event("event", cfg, "task.completed") is True

    def test_event_no_match(self):
        cfg = {"event_type": "task.completed"}
        assert self.engine.matches_event("event", cfg, "task.created") is False

    def test_non_event_trigger_does_not_match(self):
        cfg = {"event_type": "task.completed"}
        assert self.engine.matches_event("schedule", cfg, "task.completed") is False

    def test_interval_invalid_returns_none(self):
        cfg = {"interval_minutes": -5}
        result = self.engine.compute_next_run("interval", cfg)
        assert result is None

    def test_unknown_trigger_type(self):
        result = self.engine.compute_next_run("unknown_type", {})
        assert result is None

    def test_deadline_fires_within_window(self):
        now = datetime.now(timezone.utc)
        due = now + timedelta(hours=10)   # 10h from now, window is 24h
        assert self.engine.deadline_fires({"deadline_hours": 24}, due) is True

    def test_deadline_not_fired_outside_window(self):
        now = datetime.now(timezone.utc)
        due = now + timedelta(hours=30)   # 30h from now, window is 24h
        assert self.engine.deadline_fires({"deadline_hours": 24}, due) is False


# ──────────────────────────────────────────────────────────────
# 2. Condition Engine
# ──────────────────────────────────────────────────────────────

class TestConditionEngine:

    def setup_method(self):
        self.engine = ConditionEngine()
        self.ctx = {
            "overdue_tasks": 3,
            "pending_tasks": 10,
            "completed_tasks": 5,
            "total_tasks": 15,
            "day_of_week": "mon",
            "hour_of_day": 9,
        }

    def _eval(self, conditions):
        return self.engine.evaluate(conditions, db=None, user_id=1, context_override=self.ctx)

    def test_empty_conditions_passes(self):
        assert self._eval([]) is True

    def test_gt_passes(self):
        assert self._eval([{"field": "overdue_tasks", "operator": ">", "value": 0}]) is True

    def test_gt_fails(self):
        assert self._eval([{"field": "overdue_tasks", "operator": ">", "value": 5}]) is False

    def test_eq_passes(self):
        assert self._eval([{"field": "day_of_week", "operator": "==", "value": "mon"}]) is True

    def test_eq_fails(self):
        assert self._eval([{"field": "day_of_week", "operator": "==", "value": "fri"}]) is False

    def test_in_operator(self):
        assert self._eval([{"field": "day_of_week", "operator": "in", "value": ["mon", "tue"]}]) is True

    def test_not_in_operator(self):
        assert self._eval([{"field": "day_of_week", "operator": "not_in", "value": ["sat", "sun"]}]) is True

    def test_contains_operator(self):
        assert self._eval([{"field": "day_of_week", "operator": "contains", "value": "on"}]) is True

    def test_multiple_conditions_all_must_pass(self):
        conds = [
            {"field": "overdue_tasks", "operator": ">", "value": 0},
            {"field": "pending_tasks", "operator": ">=", "value": 5},
        ]
        assert self._eval(conds) is True

    def test_multiple_conditions_one_fails(self):
        conds = [
            {"field": "overdue_tasks", "operator": ">", "value": 0},
            {"field": "pending_tasks", "operator": ">", "value": 50},  # fails
        ]
        assert self._eval(conds) is False

    def test_unsupported_field_returns_false(self):
        assert self._eval([{"field": "nonexistent_field", "operator": "==", "value": 1}]) is False


# ──────────────────────────────────────────────────────────────
# 3. Execution Engine
# ──────────────────────────────────────────────────────────────

class TestExecutionEngine:

    def setup_method(self):
        self.engine = ExecutionEngine()

    def _mock_db(self, user_id: int, automation: Automation):
        db = MagicMock(spec=Session)
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    def test_disabled_automation_skipped(self, db_session):
        auto = _make_automation(db_session, user_id=1, enabled=False)
        run = self.engine.execute(auto, db_session, trigger_source="test")
        assert run.status == "skipped"

    def test_no_actions_still_completes(self, db_session):
        auto = _make_automation(db_session, user_id=1, actions=[])
        run = self.engine.execute(auto, db_session, trigger_source="test")
        assert run.status == "completed"

    def test_action_success(self, db_session):
        actions = [{"tool_name": "list_tasks", "arguments": {}}]
        auto = _make_automation(db_session, user_id=1, actions=actions)

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {"tasks": []}

        with patch("app.automation.execution_engine.tool_executor.execute", return_value=mock_result):
            run = self.engine.execute(auto, db_session, trigger_source="test")

        assert run.status == "completed"
        assert run.actions_completed == 1
        assert run.actions_attempted == 1

    def test_action_failure_stop_policy(self, db_session):
        actions = [
            {"tool_name": "create_note", "arguments": {}},
            {"tool_name": "remember", "arguments": {}},
        ]
        auto = _make_automation(db_session, user_id=1, actions=actions, failure_policy="stop")

        mock_fail = MagicMock()
        mock_fail.success = False
        mock_fail.error = MagicMock()
        mock_fail.error.message = "Tool failed"

        with patch("app.automation.execution_engine.tool_executor.execute", return_value=mock_fail):
            run = self.engine.execute(auto, db_session, trigger_source="test")

        assert run.status == "failed"
        # Only first action attempted because failure_policy="stop"
        assert run.actions_attempted == 1
        assert run.actions_completed == 0

    def test_action_failure_continue_policy(self, db_session):
        actions = [
            {"tool_name": "create_note", "arguments": {}},
            {"tool_name": "remember", "arguments": {}},
        ]
        auto = _make_automation(db_session, user_id=1, actions=actions, failure_policy="continue")

        call_count = [0]
        def side_effect(tool_name, arguments, context, bypass_confirmation):
            call_count[0] += 1
            r = MagicMock()
            r.success = (tool_name == "remember")
            r.data = {}
            r.error = MagicMock(); r.error.message = "fail"
            return r

        with patch("app.automation.execution_engine.tool_executor.execute", side_effect=side_effect):
            run = self.engine.execute(auto, db_session, trigger_source="test")

        assert run.status == "partial"
        assert run.actions_attempted == 2
        assert run.actions_completed == 1

    def test_recursion_depth_blocked(self, db_session):
        auto = _make_automation(db_session, user_id=1)
        run = self.engine.execute(auto, db_session, trigger_source="test", depth=3)
        assert run.status == "skipped"
        assert "depth" in run.error_message.lower()

    def test_conditions_gate(self, db_session):
        conditions = [{"field": "overdue_tasks", "operator": ">", "value": 100}]
        auto = _make_automation(db_session, user_id=1, conditions=conditions)

        with patch("app.automation.execution_engine.condition_engine.evaluate", return_value=False):
            run = self.engine.execute(auto, db_session, trigger_source="test")

        assert run.status == "skipped"


# ──────────────────────────────────────────────────────────────
# 4. Automation Service (unit)
# ──────────────────────────────────────────────────────────────

class TestAutomationService:

    def setup_method(self):
        self.svc = AutomationService()

    def test_create_and_get(self, db_session):
        data = AutomationCreate(
            name="Daily Brief",
            trigger_type="schedule",
            trigger_config=TriggerConfig(time="08:00"),
            actions=[ActionStep(tool_name="list_tasks", arguments={})],
        )
        auto = self.svc.create(db_session, user_id=1, data=data)
        assert auto.id is not None
        assert auto.name == "Daily Brief"
        assert auto.trigger_type == "schedule"

        fetched = self.svc.get_one(db_session, user_id=1, automation_id=auto.id)
        assert fetched.id == auto.id

    def test_get_returns_none_for_other_user(self, db_session):
        data = AutomationCreate(name="Test", trigger_type="interval",
                                trigger_config=TriggerConfig(interval_minutes=60))
        auto = self.svc.create(db_session, user_id=1, data=data)
        result = self.svc.get_one(db_session, user_id=99, automation_id=auto.id)
        assert result is None

    def test_update(self, db_session):
        data = AutomationCreate(name="Old Name", trigger_type="interval",
                                trigger_config=TriggerConfig(interval_minutes=60))
        auto = self.svc.create(db_session, user_id=1, data=data)

        updated = self.svc.update(
            db_session, auto,
            AutomationUpdate(name="New Name", enabled=False)
        )
        assert updated.name == "New Name"
        assert updated.enabled is False

    def test_delete(self, db_session):
        data = AutomationCreate(name="To Delete", trigger_type="interval",
                                trigger_config=TriggerConfig(interval_minutes=60))
        auto = self.svc.create(db_session, user_id=1, data=data)
        auto_id = auto.id
        self.svc.delete(db_session, auto)
        assert self.svc.get_one(db_session, user_id=1, automation_id=auto_id) is None

    def test_enable_disable(self, db_session):
        data = AutomationCreate(name="Toggle", trigger_type="schedule",
                                trigger_config=TriggerConfig(time="10:00"), enabled=False)
        auto = self.svc.create(db_session, user_id=1, data=data)
        # Explicitly disable first
        db_session.query(Automation).filter(Automation.id == auto.id).update({"enabled": False})
        db_session.commit(); db_session.refresh(auto)

        enabled = self.svc.enable(db_session, auto)
        assert enabled.enabled is True

        disabled = self.svc.disable(db_session, enabled)
        assert disabled.enabled is False

    def test_preview(self, db_session):
        data = AutomationCreate(
            name="Preview Test",
            trigger_type="schedule",
            trigger_config=TriggerConfig(time="08:00"),
            actions=[ActionStep(tool_name="list_tasks", arguments={})],
        )
        auto = self.svc.create(db_session, user_id=1, data=data)
        preview = self.svc.preview(auto)
        assert "next_run_at" in preview
        assert preview["estimated_action_count"] == 1

    def test_fire_event_no_matching(self, db_session):
        data = AutomationCreate(
            name="Event Auto",
            trigger_type="event",
            trigger_config=TriggerConfig(event_type="task.completed"),
        )
        self.svc.create(db_session, user_id=1, data=data)
        runs = self.svc.fire_event(db_session, user_id=1, event_type="task.created")
        assert len(runs) == 0

    def test_fire_event_matching(self, db_session):
        data = AutomationCreate(
            name="Event Auto 2",
            trigger_type="event",
            trigger_config=TriggerConfig(event_type="task.completed"),
            actions=[ActionStep(tool_name="list_tasks", arguments={})],
        )
        self.svc.create(db_session, user_id=1, data=data)

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {}

        with patch("app.automation.execution_engine.tool_executor.execute", return_value=mock_result):
            runs = self.svc.fire_event(db_session, user_id=1, event_type="task.completed")
        assert len(runs) >= 1


# ──────────────────────────────────────────────────────────────
# 5. API Endpoints
# ──────────────────────────────────────────────────────────────

class TestAutomationAPI:

    def test_create_automation(self, client, auth_headers):
        payload = {
            "name": "Morning Digest",
            "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
            "timezone": "Asia/Kolkata",
            "failure_policy": "stop",
        }
        resp = client.post("/automation/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Morning Digest"
        assert data["trigger_type"] == "schedule"
        assert data["id"] is not None

    def test_list_automations(self, client, auth_headers):
        client.post("/automation/", json={
            "name": "Auto 1", "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 60},
        }, headers=auth_headers)
        resp = client.get("/automation/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_single(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Single Get", "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 30},
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        resp = client.get(f"/automation/{auto_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == auto_id

    def test_get_404_for_nonexistent(self, client, auth_headers):
        resp = client.get("/automation/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_automation(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Update Me", "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 60},
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        resp = client.put(f"/automation/{auto_id}", json={"name": "Updated Name"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_delete_automation(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Delete Me", "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 60},
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        resp = client.delete(f"/automation/{auto_id}", headers=auth_headers)
        assert resp.status_code == 200
        # Confirm gone
        assert client.get(f"/automation/{auto_id}", headers=auth_headers).status_code == 404

    def test_enable_disable(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Toggle API", "trigger_type": "schedule",
            "trigger_config": {"time": "12:00"},
        }, headers=auth_headers)
        auto_id = r.json()["id"]

        dis = client.post(f"/automation/{auto_id}/disable", headers=auth_headers)
        assert dis.status_code == 200
        assert dis.json()["enabled"] is False

        en = client.post(f"/automation/{auto_id}/enable", headers=auth_headers)
        assert en.status_code == 200
        assert en.json()["enabled"] is True

    def test_manual_run(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Manual Run", "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=auth_headers)
        auto_id = r.json()["id"]

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = {"tasks": []}

        with patch("app.automation.execution_engine.tool_executor.execute", return_value=mock_result):
            resp = client.post(f"/automation/{auto_id}/run", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["automation_id"] == auto_id
        assert data["status"] in ("completed", "partial", "failed", "skipped")

    def test_get_runs(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "History Test", "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 30},
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        resp = client.get(f"/automation/{auto_id}/runs", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_preview(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Preview API", "trigger_type": "schedule",
            "trigger_config": {"time": "09:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        resp = client.get(f"/automation/{auto_id}/preview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "next_run_at" in data
        assert "actions" in data

    def test_fire_event_api(self, client, auth_headers):
        resp = client.post("/automation/event", json={
            "type": "task.completed",
            "payload": {"task_id": 1}
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert "automations_triggered" in resp.json()

    def test_unauthorized_access(self, client):
        resp = client.get("/automation/")
        assert resp.status_code in (401, 403)


# ──────────────────────────────────────────────────────────────
# 6. Timezone-aware scheduling
# ──────────────────────────────────────────────────────────────

class TestTimezoneScheduling:

    def test_daily_schedule_converts_local_time_to_utc(self):
        from zoneinfo import ZoneInfo
        after = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
        result = TriggerEngine().compute_next_run(
            "schedule", {"time": "08:00"}, after=after, timezone_name="Asia/Kolkata"
        )
        assert result is not None
        # 08:00 IST == 02:30 UTC
        assert (result.hour, result.minute) == (2, 30)
        assert result.tzinfo is not None
        # ...and still 08:00 in the user's timezone
        assert result.astimezone(ZoneInfo("Asia/Kolkata")).hour == 8

    def test_dst_change_keeps_local_scheduled_time(self):
        engine = TriggerEngine()
        winter = engine.compute_next_run(
            "schedule", {"time": "08:00"},
            after=datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc),
            timezone_name="America/New_York",
        )
        summer = engine.compute_next_run(
            "schedule", {"time": "08:00"},
            after=datetime(2026, 7, 6, 0, 0, tzinfo=timezone.utc),
            timezone_name="America/New_York",
        )
        assert (winter.hour, winter.minute) == (13, 0)  # EST = UTC-5
        assert (summer.hour, summer.minute) == (12, 0)  # EDT = UTC-4

    def test_one_time_naive_datetime_uses_automation_timezone(self):
        after = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = TriggerEngine().compute_next_run(
            "onetime", {"run_at": "2026-01-02T19:00:00"},
            after=after, timezone_name="Asia/Kolkata",
        )
        assert result is not None
        assert (result.hour, result.minute) == (13, 30)

    def test_invalid_timezone_rejected(self):
        from app.automation.trigger_engine import validate_timezone
        with pytest.raises(ValueError):
            validate_timezone("Mars/Olympus")

    def test_invalid_trigger_definitions_rejected(self):
        from app.automation.trigger_engine import trigger_engine
        with pytest.raises(ValueError):
            trigger_engine.validate("schedule", {"time": "not-a-time"}, "Asia/Kolkata")
        with pytest.raises(ValueError):
            trigger_engine.validate("schedule", {}, "Asia/Kolkata")
        with pytest.raises(ValueError):
            trigger_engine.validate("unknown_type", {}, "Asia/Kolkata")
        with pytest.raises(ValueError):
            trigger_engine.validate("interval", {"interval_minutes": 0}, "Asia/Kolkata")


# ──────────────────────────────────────────────────────────────
# 7. Idempotency
# ──────────────────────────────────────────────────────────────

class TestIdempotency:

    def test_same_execution_key_runs_only_once(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        engine = ExecutionEngine()
        mock = MagicMock()
        mock.success = True
        mock.data = {"tasks": []}

        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=mock):
            first = engine.execute(
                auto, db_session, trigger_source="scheduler",
                execution_key="schedule:2026-01-01T08:00:00",
            )
            second = engine.execute(
                auto, db_session, trigger_source="scheduler",
                execution_key="schedule:2026-01-01T08:00:00",
            )

        assert first.id == second.id
        count = (
            db_session.query(AutomationRun)
            .filter(AutomationRun.automation_id == auto.id)
            .count()
        )
        assert count == 1

    def test_distinct_keys_execute_separately(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        engine = ExecutionEngine()
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=mock):
            first = engine.execute(
                auto, db_session, trigger_source="manual", execution_key="manual:aaa"
            )
            second = engine.execute(
                auto, db_session, trigger_source="manual", execution_key="manual:bbb"
            )

        assert first.id != second.id


# ──────────────────────────────────────────────────────────────
# 8. Controlled retries
# ──────────────────────────────────────────────────────────────

class TestRetries:

    def _automation(self, db_session, **kwargs):
        kwargs.setdefault("max_retries", 1)
        kwargs.setdefault("retry_delay_seconds", 0)
        kwargs.setdefault("actions", [{"tool_name": "create_note", "arguments": {}}])
        return _make_automation(db_session, user_id=1, **kwargs)

    @staticmethod
    def _result(success: bool, code=None, message="boom"):
        result = MagicMock()
        result.success = success
        result.data = {} if success else None
        if not success:
            result.error = MagicMock()
            result.error.code = code
            result.error.message = message
        return result

    def test_transient_failure_is_retried(self, db_session):
        from app.tools.tool_result import ToolErrorCode

        auto = self._automation(db_session)
        fail = self._result(False, ToolErrorCode.EXECUTION_FAILED, "temporarily down")
        ok = self._result(True)

        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=[fail, ok]) as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"
        assert executor.call_count == 2
        assert run.execution_log[0]["attempts"] == 2

    def test_permission_denied_is_not_retried(self, db_session):
        from app.tools.tool_result import ToolErrorCode

        auto = self._automation(db_session)
        denied = self._result(False, ToolErrorCode.PERMISSION_DENIED, "nope")

        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=denied) as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "failed"
        assert executor.call_count == 1
        assert run.execution_log[0]["attempts"] == 1

    def test_missing_tool_is_not_retried(self, db_session):
        auto = self._automation(
            db_session,
            actions=[{"tool_name": "definitely_not_a_tool", "arguments": {}}],
        )
        assert auto.actions == [{"tool_name": "definitely_not_a_tool", "arguments": {}}]
        with patch("app.automation.execution_engine.tool_executor.execute") as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "failed"
        executor.assert_not_called()


# ──────────────────────────────────────────────────────────────
# 9. Permissions / confirmation / tool allow-list
# ──────────────────────────────────────────────────────────────

class TestAutomationSafety:

    def test_dangerous_action_is_refused_without_preapproval(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "delete_task", "arguments": {"task_id": 1}}],
        )
        with patch("app.automation.execution_engine.tool_executor.execute") as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "failed"
        assert "confirmation" in run.execution_log[0]["error"].lower()
        executor.assert_not_called()

    def test_preapproved_dangerous_action_bypasses_confirmation(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{
                "tool_name": "delete_task",
                "arguments": {"task_id": 1},
                "confirmation_policy": "preapproved",
            }],
        )
        mock = MagicMock()
        mock.success = True
        mock.data = {"deleted": True}

        with patch(
            "app.automation.execution_engine.tool_executor.execute",
            return_value=mock,
        ) as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"
        assert executor.call_count == 1
        # The user pre-approved this action, so the confirmation gate is bypassed.
        assert executor.call_args.kwargs["bypass_confirmation"] is True

    def test_confirmation_required_error_is_not_retried(self, db_session):
        """A tool that raises CONFIRMATION_REQUIRED mid-flight is never retried."""
        from app.tools.tool_result import ToolErrorCode

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        denied = MagicMock()
        denied.success = False
        denied.error = MagicMock()
        denied.error.code = ToolErrorCode.CONFIRMATION_REQUIRED
        denied.error.message = "needs confirmation"
        denied.requires_confirmation = True

        with patch(
            "app.automation.execution_engine.tool_executor.execute",
            return_value=denied,
        ) as executor:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "failed"
        assert executor.call_count == 1
        assert "confirmation" in run.execution_log[0]["error"].lower()

    def test_empty_action_list_is_rejected_at_creation(self, db_session):
        from app.automation.automation_service import AutomationService

        svc = AutomationService()
        with pytest.raises(ValueError):
            svc.validate_definition("schedule", {"time": "08:00"}, [], ["not-a-dict"], "UTC")


# ──────────────────────────────────────────────────────────────
# 10. Creation-time validation (API)
# ──────────────────────────────────────────────────────────────

class TestCreationValidation:
    """Every invalid definition must be rejected before it is persisted."""

    BASE = {
        "name": "Validate Me",
        "trigger_type": "schedule",
        "trigger_config": {"time": "08:00"},
        "timezone": "Asia/Kolkata",
    }

    def _post(self, client, headers, **overrides):
        return client.post("/automation/", json={**self.BASE, **overrides}, headers=headers)

    def test_valid_schedule_automation_created(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        assert r.status_code == 201, r.text
        assert r.json()["next_run_at"] is not None

    def test_missing_name_rejected(self, client, auth_headers):
        payload = {k: v for k, v in self.BASE.items() if k != "name"}
        assert client.post("/automation/", json=payload, headers=auth_headers).status_code == 422

    def test_blank_name_rejected(self, client, auth_headers):
        assert self._post(client, auth_headers, name="").status_code == 422

    def test_invalid_trigger_type_rejected(self, client, auth_headers):
        assert self._post(client, auth_headers, trigger_type="telepathy").status_code == 422

    def test_invalid_schedule_time_rejected(self, client, auth_headers):
        r = self._post(client, auth_headers, trigger_config={"time": "not-a-time"})
        assert r.status_code == 422

    def test_schedule_without_time_rejected(self, client, auth_headers):
        assert self._post(client, auth_headers, trigger_config={}).status_code == 422

    def test_invalid_weekday_rejected(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            trigger_config={"time": "08:00", "days": ["funday"]},
        )
        assert r.status_code == 422

    def test_invalid_timezone_rejected(self, client, auth_headers):
        assert self._post(client, auth_headers, timezone="Mars/Olympus").status_code == 422

    def test_invalid_failure_policy_rejected(self, client, auth_headers):
        assert self._post(client, auth_headers, failure_policy="explode").status_code == 422

    def test_unknown_action_tool_rejected(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            actions=[{"tool_name": "definitely_not_a_tool", "arguments": {}}],
        )
        assert r.status_code == 422
        assert "not registered" in r.json()["detail"]

    def test_blocked_tool_rejected(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            actions=[{"tool_name": "run_shell", "arguments": {"cmd": "rm -rf /"}}],
        )
        assert r.status_code == 422
        assert "may not be used" in r.json()["detail"]

    def test_dangerous_tool_requires_preapproval(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            actions=[{"tool_name": "delete_task", "arguments": {"task_id": 1}}],
        )
        assert r.status_code == 422
        assert "confirmation" in r.json()["detail"].lower()

    def test_dangerous_tool_preapproved_is_accepted(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            actions=[{
                "tool_name": "delete_task",
                "arguments": {"task_id": 1},
                "confirmation_policy": "preapproved",
            }],
        )
        assert r.status_code == 201, r.text

    def test_invalid_condition_field_rejected(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            conditions=[{"field": "moon_phase", "operator": "==", "value": "full"}],
        )
        assert r.status_code == 422

    def test_invalid_condition_operator_rejected(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            conditions=[{"field": "overdue_tasks", "operator": "approximately", "value": 1}],
        )
        assert r.status_code == 422

    def test_condition_group_accepted(self, client, auth_headers):
        r = self._post(
            client, auth_headers,
            conditions=[{
                "op": "and",
                "rules": [
                    {"field": "overdue_tasks", "operator": ">", "value": 0},
                    {"field": "day_of_week", "operator": "==", "value": "mon"},
                ],
            }],
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        assert r.status_code == 201, r.text
        assert r.json()["conditions"][0]["op"] == "and"

    def test_condition_group_too_deep_rejected(self, client, auth_headers):
        deep = {"op": "and", "rules": [{
            "op": "or", "rules": [{
                "op": "not", "rules": [{
                    "op": "and", "rules": [
                        {"field": "overdue_tasks", "operator": ">", "value": 0}
                    ],
                }],
            }],
        }]}
        assert self._post(client, auth_headers, conditions=[deep]).status_code == 422


# ──────────────────────────────────────────────────────────────
# 11. Condition groups (AND / OR / NOT)
# ──────────────────────────────────────────────────────────────

class TestConditionGroups:

    def setup_method(self):
        self.engine = ConditionEngine()
        self.ctx = {
            "overdue_tasks": 3,
            "pending_tasks": 10,
            "completed_tasks": 5,
            "total_tasks": 15,
            "day_of_week": "mon",
            "hour_of_day": 9,
        }

    def _eval(self, conditions):
        return self.engine.evaluate(conditions, None, 1, context_override=self.ctx)

    OVERDUE = {"field": "overdue_tasks", "operator": ">", "value": 0}
    NONE_OVERDUE = {"field": "overdue_tasks", "operator": ">", "value": 50}
    IS_MONDAY = {"field": "day_of_week", "operator": "==", "value": "mon"}
    IS_FRIDAY = {"field": "day_of_week", "operator": "==", "value": "fri"}

    def test_and_group_true(self):
        assert self._eval([{"op": "and", "rules": [self.OVERDUE, self.IS_MONDAY]}]) is True

    def test_and_group_false(self):
        assert self._eval([{"op": "and", "rules": [self.OVERDUE, self.IS_FRIDAY]}]) is False

    def test_or_group_true_when_one_matches(self):
        assert self._eval([{"op": "or", "rules": [self.NONE_OVERDUE, self.IS_MONDAY]}]) is True

    def test_or_group_false_when_none_match(self):
        assert self._eval([{"op": "or", "rules": [self.NONE_OVERDUE, self.IS_FRIDAY]}]) is False

    def test_not_group_inverts(self):
        assert self._eval([{"op": "not", "rules": [self.IS_FRIDAY]}]) is True
        assert self._eval([{"op": "not", "rules": [self.IS_MONDAY]}]) is False

    def test_nested_groups(self):
        # IF (overdue > 0 AND monday) OR NOT friday
        tree = [{
            "op": "or",
            "rules": [
                {"op": "and", "rules": [self.OVERDUE, self.IS_MONDAY]},
                {"op": "not", "rules": [self.IS_FRIDAY]},
            ],
        }]
        assert self._eval(tree) is True

    def test_flat_rules_and_group_combine(self):
        assert self._eval([self.OVERDUE, {"op": "or", "rules": [self.IS_MONDAY]}]) is True

    def test_unknown_field_raises_on_validate(self):
        with pytest.raises(ValueError):
            self.engine.validate([{"field": "nope", "operator": "==", "value": 1}])

    def test_unknown_operator_raises_on_validate(self):
        with pytest.raises(ValueError):
            self.engine.validate([{"field": "overdue_tasks", "operator": "~=", "value": 1}])

    def test_missing_value_raises_on_validate(self):
        with pytest.raises(ValueError):
            self.engine.validate([{"field": "overdue_tasks", "operator": ">"}])

    def test_group_without_rules_raises(self):
        with pytest.raises(ValueError):
            self.engine.validate([{"op": "and", "rules": []}])

    def test_unknown_group_operator_raises(self):
        with pytest.raises(ValueError):
            self.engine.validate([{"op": "xor", "rules": [self.OVERDUE]}])

    def test_depth_limit_enforced(self):
        node = self.OVERDUE
        for _ in range(4):
            node = {"op": "and", "rules": [node]}
        with pytest.raises(ValueError):
            self.engine.validate([node])

    def test_invalid_tree_is_false_at_evaluation(self):
        # Evaluation must never raise — it fails closed.
        assert self._eval([{"field": "ghost", "operator": "==", "value": 1}]) is False

    def test_context_snapshot_is_per_user(self):
        """build_context must only ever count the owning user's tasks."""
        from app.database.connection import SessionLocal
        from app.models.task import Task

        db = SessionLocal()
        try:
            user_a = _app_user(db)
            user_b = _app_user(db)
            db.add(Task(user_id=user_a.id, title="A open"))
            db.add(Task(user_id=user_a.id, title="A done", completed=True))
            db.add(Task(user_id=user_b.id, title="B open"))
            db.commit()

            ctx_a = ConditionEngine().build_context(db, user_a.id)
            ctx_b = ConditionEngine().build_context(db, user_b.id)
        finally:
            db.close()

        assert ctx_a["total_tasks"] == 2
        assert ctx_a["pending_tasks"] == 1
        assert ctx_b["total_tasks"] == 1
        assert ctx_b["pending_tasks"] == 1


# ──────────────────────────────────────────────────────────────
# 12. User isolation
# ──────────────────────────────────────────────────────────────

def _second_user_headers(client):
    """Register + log in a second, independent user."""
    from uuid import uuid4

    suffix = uuid4().hex[:8]
    client.post("/register", json={
        "username": f"other_{suffix}",
        "email": f"other_{suffix}@rajos.io",
        "password": "TestPassword123!",
    })
    resp = client.post("/login", json={
        "email": f"other_{suffix}@rajos.io",
        "password": "TestPassword123!",
    })
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestUserIsolation:
    """User A must never see, run or modify user B's automations."""

    def _automation_of_user_a(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Private Automation",
            "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=auth_headers)
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def test_other_user_list_does_not_include_it(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        ids = [a["id"] for a in client.get("/automation/", headers=other).json()]
        assert auto_id not in ids

    def test_other_user_cannot_read(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.get(f"/automation/{auto_id}", headers=other).status_code == 404

    def test_other_user_cannot_update(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        r = client.put(f"/automation/{auto_id}", json={"name": "Hijacked"}, headers=other)
        assert r.status_code == 404
        still = client.get(f"/automation/{auto_id}", headers=auth_headers).json()
        assert still["name"] == "Private Automation"

    def test_other_user_cannot_delete(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.delete(f"/automation/{auto_id}", headers=other).status_code == 404
        assert client.get(f"/automation/{auto_id}", headers=auth_headers).status_code == 200

    def test_other_user_cannot_run(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.post(f"/automation/{auto_id}/run", headers=other).status_code == 404

    def test_other_user_cannot_cancel(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.post(f"/automation/{auto_id}/cancel", headers=other).status_code == 404

    def test_other_user_cannot_toggle(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.post(f"/automation/{auto_id}/disable", headers=other).status_code == 404
        assert client.post(f"/automation/{auto_id}/enable", headers=other).status_code == 404

    def test_other_user_cannot_read_history(self, client, auth_headers):
        auto_id = self._automation_of_user_a(client, auth_headers)
        other = _second_user_headers(client)
        assert client.get(f"/automation/{auto_id}/runs", headers=other).status_code == 404

    def test_events_only_trigger_the_owners_automations(self, client, auth_headers):
        self._automation_of_user_a(client, auth_headers)  # schedule trigger
        r = client.post("/automation/", json={
            "name": "A event automation",
            "trigger_type": "event",
            "trigger_config": {"event_type": "task.completed"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=auth_headers)
        assert r.status_code == 201

        other = _second_user_headers(client)
        resp = client.post("/automation/event", json={"type": "task.completed"}, headers=other)
        assert resp.status_code == 200
        assert resp.json()["automations_triggered"] == 0

    def test_unauthenticated_requests_are_rejected(self, client):
        for method, path in (
            ("get", "/automation/"),
            ("post", "/automation/"),
            ("get", "/automation/1"),
            ("put", "/automation/1"),
            ("delete", "/automation/1"),
            ("post", "/automation/1/run"),
            ("post", "/automation/1/cancel"),
            ("get", "/automation/1/runs"),
        ):
            resp = getattr(client, method)(path)
            assert resp.status_code in (401, 403), f"{method} {path} → {resp.status_code}"

    def test_user_supplied_user_id_is_ignored(self, client, auth_headers):
        """An extra user_id in the payload must not reassign ownership."""
        victim = _second_user_headers(client)  # ensure a second user exists
        r = client.post("/automation/", json={
            "name": "Ownership Probe",
            "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 30},
            "user_id": 999999,
        }, headers=auth_headers)
        assert r.status_code == 201, r.text
        victim_ids = [a["id"] for a in client.get("/automation/", headers=victim).json()]
        assert r.json()["id"] not in victim_ids


# ──────────────────────────────────────────────────────────────
# 13. Tool permission enforcement (Tool Registry)
# ──────────────────────────────────────────────────────────────

class TestToolPermissionEnforcement:

    def test_disabled_tool_refused_at_creation(self, client, auth_headers):
        from app.tools.tool_registry import tool_registry

        tool = tool_registry.get_tool("list_tasks")
        original = tool.enabled
        tool.enabled = False
        try:
            r = client.post("/automation/", json={
                "name": "Disabled tool",
                "trigger_type": "schedule",
                "trigger_config": {"time": "08:00"},
                "actions": [{"tool_name": "list_tasks", "arguments": {}}],
            }, headers=auth_headers)
            assert r.status_code == 422
            assert "disabled" in r.json()["detail"].lower()
        finally:
            tool.enabled = original

    def test_disabled_tool_refused_at_run(self, db_session):
        from app.tools.tool_registry import tool_registry

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        tool = tool_registry.get_tool("list_tasks")
        original = tool.enabled
        tool.enabled = False
        try:
            with patch("app.automation.execution_engine.tool_executor.execute") as executor:
                run = ExecutionEngine().execute(auto, db_session)
            executor.assert_not_called()
        finally:
            tool.enabled = original

        assert run.status == "failed"
        assert "disabled" in run.execution_log[0]["error"].lower()

    def test_blocked_tool_never_reaches_the_executor(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "run_shell", "arguments": {"cmd": "whoami"}}],
        )
        with patch("app.automation.execution_engine.tool_executor.execute") as executor:
            run = ExecutionEngine().execute(auto, db_session)

        executor.assert_not_called()
        assert run.status == "failed"
        assert "may not be used" in run.execution_log[0]["error"]

    def test_stored_owner_arguments_cannot_be_injected(self, db_session):
        """user_id in stored action args is stripped — ownership is the owner's."""
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{
                "tool_name": "list_tasks",
                "arguments": {"user_id": 4242, "limit": 5},
            }],
        )
        captured = {}

        def side_effect(tool_name, arguments, context, bypass_confirmation):
            captured["arguments"] = arguments
            captured["user_id"] = context.user_id
            r = MagicMock()
            r.success = True
            r.data = {}
            return r

        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=side_effect):
            ExecutionEngine().execute(auto, db_session)

        assert "user_id" not in captured["arguments"]
        assert captured["user_id"] == 1


# ──────────────────────────────────────────────────────────────
# 14. Scheduler behaviour, persistence and restart recovery
# ──────────────────────────────────────────────────────────────

class TestSchedulerBehaviour:
    """Scheduler tests use the shared application database (temp file)."""

    @staticmethod
    def _tick():
        import asyncio
        from app.automation.scheduler import AutomationScheduler

        sched = AutomationScheduler()
        sched._running = True
        asyncio.run(sched._tick())

    def _automation(self, db, user, **kwargs):
        defaults = dict(
            user_id=user.id,
            name="Scheduler Test",
            trigger_type="schedule",
            trigger_config={"time": "08:00"},
            conditions=[],
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
            timezone="UTC",
            failure_policy="stop",
            enabled=True,
            max_retries=0,
            retry_delay_seconds=0,
        )
        defaults.update(kwargs)
        auto = Automation(**defaults)
        db.add(auto)
        db.commit()
        db.refresh(auto)
        return auto

    def test_due_automation_is_executed_and_advances(self):
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(
                db, user,
                next_run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            auto = db.get(Automation, auto_id)
            runs = db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).all()
            assert len(runs) == 1
            assert runs[0].status == "completed"
            assert runs[0].trigger_source == "scheduler"
            assert auto.last_run_at is not None
            assert auto.next_run_at is not None
            assert auto.next_run_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
        finally:
            db.close()

    def test_missed_run_fires_once_and_does_not_hot_loop(self):
        """A schedule that was missed for days runs once, then reschedules."""
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(
                db, user,
                next_run_at=datetime.now(timezone.utc) - timedelta(days=3),
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            runs = db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).all()
            assert len(runs) == 1
            auto = db.get(Automation, auto_id)
            assert auto.next_run_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)
        finally:
            db.close()

    def test_disabled_automation_is_ignored(self):
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(
                db, user, enabled=False,
                next_run_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            assert db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).count() == 0
        finally:
            db.close()

    def test_event_automation_is_not_polled(self):
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(
                db, user, trigger_type="event",
                trigger_config={"event_type": "task.completed"},
                next_run_at=datetime.now(timezone.utc) - timedelta(minutes=5),
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            assert db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).count() == 0
        finally:
            db.close()

    def test_one_time_automation_disables_itself_after_firing(self):
        db = _app_session()
        try:
            user = _app_user(db)
            run_at = datetime.now(timezone.utc) - timedelta(minutes=2)
            auto = self._automation(
                db, user,
                trigger_type="onetime",
                trigger_config={"run_at": run_at.isoformat()},
                next_run_at=run_at,
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            auto = db.get(Automation, auto_id)
            assert auto.enabled is False
            assert auto.next_run_at is None
            assert db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).count() == 1
        finally:
            db.close()

    def test_schedule_survives_a_restart(self):
        """After a process restart the automation is still scheduled."""
        from app.automation.automation_schemas import AutomationCreate, TriggerConfig
        from app.automation.automation_service import AutomationService

        db = _app_session()
        try:
            user = _app_user(db)
            auto = AutomationService().create(db, user.id, AutomationCreate(
                name="Survives Restart",
                trigger_type="schedule",
                trigger_config=TriggerConfig(time="08:00", days=["mon", "tue"]),
                timezone="Asia/Kolkata",
            ))
            auto_id = auto.id
            first_next_run = auto.next_run_at
        finally:
            db.close()

        # Simulate a full restart: every in-memory object is gone, and a brand
        # new scheduler instance starts up against the same database.
        from app.automation.scheduler import AutomationScheduler
        fresh_scheduler = AutomationScheduler()
        fresh_scheduler._running = True

        db = _app_session()
        try:
            auto = db.get(Automation, auto_id)
            assert auto is not None, "automation disappeared across restart"
            assert auto.enabled is True
            assert auto.trigger_type == "schedule"
            assert auto.trigger_config["time"] == "08:00"
            assert auto.timezone == "Asia/Kolkata"
            assert auto.next_run_at is not None
            assert auto.next_run_at.isoformat() == first_next_run.isoformat()
        finally:
            db.close()

    def test_interrupted_runs_are_failed_on_restart(self):
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(db, user)
            stuck = AutomationRun(
                automation_id=auto.id,
                user_id=user.id,
                status="running",
                trigger_source="scheduler",
                execution_key=f"stuck:{auto.id}",
            )
            db.add(stuck)
            db.commit()
            run_id = stuck.id
        finally:
            db.close()

        from app.automation.scheduler import AutomationScheduler
        AutomationScheduler._recover_interrupted_runs()

        db = _app_session()
        try:
            recovered = db.get(AutomationRun, run_id)
            assert recovered.status == "failed"
            assert "restart" in (recovered.error_message or "").lower()
            assert recovered.completed_at is not None
        finally:
            db.close()

    def test_deadline_automation_fires_once_per_task_window(self):
        from app.models.task import Task

        db = _app_session()
        try:
            user = _app_user(db)
            task = Task(
                user_id=user.id,
                title="Due soon",
                due_date=datetime.utcnow() + timedelta(hours=5),
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            task_id = task.id
            auto = self._automation(
                db, user,
                trigger_type="deadline",
                trigger_config={"deadline_hours": 24, "poll_minutes": 15},
                next_run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            )
            auto_id = auto.id
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            first = db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).all()
            assert len(first) == 1
            assert first[0].trigger_source == f"deadline:task:{task_id}"
            # Force the schedule back to "due" and poll again: the same
            # (task, due date) pair must not produce a second run.
            auto = db.get(Automation, auto_id)
            auto.next_run_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            db.commit()
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            assert db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).count() == 1
        finally:
            db.close()

    def test_archived_automation_is_never_executed(self):
        db = _app_session()
        try:
            user = _app_user(db)
            auto = self._automation(
                db, user,
                next_run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            )
            auto_id = auto.id
            # Archived but still flagged enabled (worst case for the scheduler).
            auto.archived_at = datetime.now(timezone.utc)
            auto.enabled = True
            db.commit()
        finally:
            db.close()

        self._tick()

        db = _app_session()
        try:
            assert db.query(AutomationRun).filter(
                AutomationRun.automation_id == auto_id
            ).count() == 0
        finally:
            db.close()


# ──────────────────────────────────────────────────────────────
# 15. Cancellation
# ──────────────────────────────────────────────────────────────

class TestCancellation:

    def test_cancel_stops_remaining_actions(self, db_session):
        from app.automation import execution_engine as ee

        auto = _make_automation(
            db_session, user_id=1,
            actions=[
                {"tool_name": "create_note", "arguments": {"title": "one"}},
                {"tool_name": "create_note", "arguments": {"title": "two"}},
                {"tool_name": "create_note", "arguments": {"title": "three"}},
            ],
        )
        executed = []

        def side_effect(tool_name, arguments, context, bypass_confirmation):
            executed.append(arguments.get("title"))
            ee.request_cancel(auto.id)  # user hits Cancel while action 1 runs
            r = MagicMock()
            r.success = True
            r.data = {}
            return r

        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=side_effect):
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "cancelled"
        assert run.actions_attempted == 1
        assert executed == ["one"]
        assert "cancelled" in (run.error_message or "").lower()

    def test_cancel_does_not_leak_into_the_next_run(self, db_session):
        from app.automation import execution_engine as ee

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        ee.request_cancel(auto.id)  # stale flag left over from an earlier cancel
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=mock):
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"

    def test_cancelled_run_is_visible_in_history(self, db_session):
        from app.automation import execution_engine as ee
        from app.automation.automation_service import AutomationService

        auto = _make_automation(
            db_session, user_id=1,
            actions=[
                {"tool_name": "create_note", "arguments": {"title": "one"}},
                {"tool_name": "create_note", "arguments": {"title": "two"}},
            ],
        )

        def side_effect(tool_name, arguments, context, bypass_confirmation):
            ee.request_cancel(auto.id)
            r = MagicMock()
            r.success = True
            r.data = {}
            return r

        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=side_effect):
            result = ExecutionEngine().execute(auto, db_session)

        assert result.status == "cancelled"
        runs = AutomationService().get_runs(db_session, auto.id, user_id=1)
        assert len(runs) == 1
        assert runs[0].status == "cancelled"
        assert runs[0].completed_at is not None

    def test_persisted_cancelled_status_is_detected(self, db_session):
        """The DB run status is the cross-worker cancellation signal."""
        auto = _make_automation(db_session, user_id=1)
        run = AutomationRun(
            automation_id=auto.id,
            user_id=1,
            status="cancelled",
            trigger_source="scheduler",
        )
        db_session.add(run)
        db_session.commit()
        db_session.refresh(run)

        assert ExecutionEngine._is_cancelled(auto, db_session, run) is True

        run.status = "running"
        db_session.commit()
        assert ExecutionEngine._is_cancelled(auto, db_session, run) is False

    def test_cancel_endpoint_with_nothing_in_flight(self, client, auth_headers):
        r = client.post("/automation/", json={
            "name": "Cancel Me",
            "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 60},
        }, headers=auth_headers)
        auto_id = r.json()["id"]

        resp = client.post(f"/automation/{auto_id}/cancel", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cancelled_runs"] == 0

    def test_cancel_marks_stuck_running_run(self, client, auth_headers, db_session):
        r = client.post("/automation/", json={
            "name": "Stuck Run",
            "trigger_type": "interval",
            "trigger_config": {"interval_minutes": 60},
        }, headers=auth_headers)
        auto_id = r.json()["id"]
        automation = db_session.get(Automation, auto_id)

        stuck = AutomationRun(
            automation_id=automation.id,
            user_id=automation.user_id,
            status="running",
            trigger_source="scheduler",
            execution_key="stuck-1",
        )
        db_session.add(stuck)
        db_session.commit()

        resp = client.post(f"/automation/{auto_id}/cancel", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["cancelled_runs"] == 1
        db_session.refresh(stuck)
        assert stuck.status == "cancelled"


# ──────────────────────────────────────────────────────────────
# 16. Burst rate limiting
# ──────────────────────────────────────────────────────────────

class TestRateLimiting:

    def test_burst_is_capped(self, db_session):
        from app.automation import execution_engine as ee

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        with patch.object(ee, "_MAX_RUNS_PER_WINDOW", 3), \
                patch.object(ee, "_RUN_TIMESTAMPS", {}), \
                patch("app.automation.execution_engine.tool_executor.execute",
                      return_value=mock):
            statuses = [
                ExecutionEngine().execute(
                    auto, db_session, execution_key=f"burst:{i}"
                ).status
                for i in range(6)
            ]

        assert statuses[:3] == ["completed", "completed", "completed"]
        assert set(statuses[3:]) == {"skipped"}

    def test_rate_limited_run_records_a_reason(self, db_session):
        from app.automation import execution_engine as ee

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        with patch.object(ee, "_MAX_RUNS_PER_WINDOW", 1), \
                patch.object(ee, "_RUN_TIMESTAMPS", {}), \
                patch("app.automation.execution_engine.tool_executor.execute",
                      return_value=mock):
            ExecutionEngine().execute(auto, db_session, execution_key="rl:1")
            limited = ExecutionEngine().execute(auto, db_session, execution_key="rl:2")

        assert limited.status == "skipped"
        assert "rate limited" in (limited.error_message or "").lower()

    def test_each_automation_has_its_own_budget(self, db_session):
        from app.automation import execution_engine as ee

        auto_a = _make_automation(
            db_session, user_id=1, name="A",
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        auto_b = _make_automation(
            db_session, user_id=1, name="B",
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        with patch.object(ee, "_MAX_RUNS_PER_WINDOW", 2), \
                patch.object(ee, "_RUN_TIMESTAMPS", {}), \
                patch("app.automation.execution_engine.tool_executor.execute",
                      return_value=mock):
            for i in range(2):
                assert ExecutionEngine().execute(
                    auto_a, db_session, execution_key=f"a:{i}"
                ).status == "completed"
            # B is unaffected by A exhausting its budget.
            assert ExecutionEngine().execute(
                auto_b, db_session, execution_key="b:0"
            ).status == "completed"


# ──────────────────────────────────────────────────────────────
# 17. Recursion / loop protection
# ──────────────────────────────────────────────────────────────

class TestRecursionProtection:

    def test_self_triggering_automation_is_blocked(self, db_session):
        from app.automation.automation_service import automation_service

        # Dedicated owner so the event cannot wake up automations other tests left behind.
        owner = _unique_user_id()
        auto = _make_automation(
            db_session, user_id=owner,
            trigger_type="event",
            trigger_config={"event_type": "task.completed"},
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        nested = []

        def side_effect(tool_name, arguments, context, bypass_confirmation):
            # The action emits the very event that triggered this automation.
            nested.extend(automation_service.fire_event(
                db_session, user_id=owner, event_type="task.completed",
                event_id=f"chain-{len(nested)}",
            ))
            r = MagicMock()
            r.success = True
            r.data = {}
            return r

        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=side_effect):
            run = ExecutionEngine().execute(
                auto, db_session,
                trigger_source="event:task.completed",
                execution_key="evt-1",
            )

        assert run.status == "completed"
        assert nested, "the recursive event chain should have been attempted"
        assert all(r.status == "skipped" for r in nested)
        assert any("loop" in (r.error_message or "").lower() for r in nested)

    def test_two_automations_do_not_chain_forever(self, db_session):
        from app.automation import execution_engine as ee
        from app.automation.automation_service import automation_service

        owner = _unique_user_id()
        auto_a = _make_automation(
            db_session, user_id=owner, name="A",
            trigger_type="event",
            trigger_config={"event_type": "task.completed"},
            actions=[{"tool_name": "list_tasks", "arguments": {"emit": "task.created"}}],
        )
        auto_b = _make_automation(
            db_session, user_id=owner, name="B",
            trigger_type="event",
            trigger_config={"event_type": "task.created"},
            actions=[{"tool_name": "list_tasks", "arguments": {"emit": "task.completed"}}],
        )
        nested = []

        def side_effect(tool_name, arguments, context, bypass_confirmation):
            event = arguments.get("emit")
            if event:
                nested.extend(automation_service.fire_event(
                    db_session, user_id=owner, event_type=event,
                    event_id=f"{event}-{len(nested)}",
                ))
            r = MagicMock()
            r.success = True
            r.data = {}
            return r

        with patch.object(ee, "_RUN_TIMESTAMPS", {}), \
                patch("app.automation.execution_engine.tool_executor.execute",
                      side_effect=side_effect):
            root = ExecutionEngine().execute(
                auto_a, db_session,
                trigger_source="event:task.completed", execution_key="chain-root",
            )

        assert root.status == "completed"
        # A → B → A(blocked).  The chain is bounded, never unbounded.
        assert len(nested) <= 5
        assert any(r.status == "skipped" for r in nested)

    def test_depth_cap_blocks_deep_chains(self, db_session):
        from app.automation import execution_engine as ee

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        mock = MagicMock()
        mock.success = True
        mock.data = {}

        # Depth 2 is still allowed, depth 3 (the cap) is not.
        token = ee._EXECUTION_DEPTH.set(2)
        try:
            with patch("app.automation.execution_engine.tool_executor.execute",
                       return_value=mock):
                allowed = ExecutionEngine().execute(auto, db_session)
        finally:
            ee._EXECUTION_DEPTH.reset(token)
        assert allowed.status == "completed"

        token = ee._EXECUTION_DEPTH.set(3)
        try:
            blocked = ExecutionEngine().execute(auto, db_session)
        finally:
            ee._EXECUTION_DEPTH.reset(token)
        assert blocked.status == "skipped"
        assert "depth" in (blocked.error_message or "").lower()


# ──────────────────────────────────────────────────────────────
# 18. Notification integration
# ──────────────────────────────────────────────────────────────

class TestNotificationIntegration:

    def _success(self):
        m = MagicMock()
        m.success = True
        m.data = {}
        return m

    def _failure(self):
        from app.tools.tool_result import ToolErrorCode

        m = MagicMock()
        m.success = False
        m.error = MagicMock()
        m.error.code = ToolErrorCode.EXECUTION_FAILED
        m.error.message = "boom"
        return m

    def test_completed_run_notifies_the_owner(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=self._success()), \
                patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"
        notify.assert_called_once()
        _user, message = notify.call_args.args[0], notify.call_args.args[1]
        assert "Test Automation" in message
        assert "completed" in message

    def test_failed_run_notifies_the_owner(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "create_note", "arguments": {}}],
            max_retries=0,
        )
        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=self._failure()), \
                patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "failed"
        notify.assert_called_once()
        assert "failed" in notify.call_args.args[1]

    def test_partial_run_reports_partial_completion(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[
                {"tool_name": "list_tasks", "arguments": {}},
                {"tool_name": "create_note", "arguments": {}},
            ],
            failure_policy="continue",
            max_retries=0,
        )
        with patch("app.automation.execution_engine.tool_executor.execute",
                   side_effect=[self._success(), self._failure()]), \
                patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "partial"
        assert "partially" in notify.call_args.args[1]

    def test_notification_failure_does_not_break_the_run(self, db_session):
        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=self._success()), \
                patch(
                    "app.notifications.notification_manager.NotificationManager.send_task_reminder",
                    side_effect=RuntimeError("sms provider down"),
                ):
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"

    def test_notifications_disabled_is_respected(self, db_session):
        from app.models.user import User

        auto = _make_automation(
            db_session, user_id=1,
            actions=[{"tool_name": "list_tasks", "arguments": {}}],
        )
        user = db_session.get(User, 1)
        user.notifications_enabled = False
        db_session.commit()

        with patch("app.automation.execution_engine.tool_executor.execute",
                   return_value=self._success()), \
                patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            run = ExecutionEngine().execute(auto, db_session)

        assert run.status == "completed"
        notify.assert_not_called()

    def test_send_notification_tool_uses_the_existing_notifier(self):
        from app.tools.tool_executor import tool_executor as real_executor
        from app.tools.tool_context import ToolExecutionContext

        # The tool resolves the user on the application database.
        db = _app_session()
        try:
            user = _app_user(db, notifications_enabled=True)
            user_id = user.id
        finally:
            db.close()

        with patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            result = real_executor.execute(
                "send_notification",
                {"message": "Your daily brief is ready."},
                ToolExecutionContext(user_id=user_id, permissions=["*"]),
            )

        assert result.success is True
        assert result.data["status"] == "sent"
        notify.assert_called_once()

    def test_send_notification_tool_respects_disabled_notifications(self):
        from app.tools.tool_executor import tool_executor as real_executor
        from app.tools.tool_context import ToolExecutionContext

        db = _app_session()
        try:
            user = _app_user(db, notifications_enabled=False)
            user_id = user.id
        finally:
            db.close()

        with patch("app.notifications.notification_manager.NotificationManager.send_task_reminder") as notify:
            result = real_executor.execute(
                "send_notification",
                {"message": "Should be suppressed"},
                ToolExecutionContext(user_id=user_id, permissions=["*"]),
            )

        assert result.success is True
        assert result.data["status"] == "skipped"
        notify.assert_not_called()


# ──────────────────────────────────────────────────────────────
# 19. Delete / edit safety and execution history
# ──────────────────────────────────────────────────────────────

class TestDeleteAndHistory:

    def _create(self, client, headers, name="History Automation"):
        r = client.post("/automation/", json={
            "name": name,
            "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=headers)
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def test_delete_preserves_execution_history(self, client, auth_headers):
        auto_id = self._create(client, auth_headers)
        run = client.post(f"/automation/{auto_id}/run", headers=auth_headers)
        assert run.status_code == 200

        deleted = client.delete(f"/automation/{auto_id}", headers=auth_headers)
        assert deleted.status_code == 200
        assert deleted.json()["archived"] is True

        # Gone from the list and its detail page...
        assert client.get(f"/automation/{auto_id}", headers=auth_headers).status_code == 404
        assert auto_id not in [
            a["id"] for a in client.get("/automation/", headers=auth_headers).json()
        ]

        # ...but the execution history is still readable.
        history = client.get(f"/automation/{auto_id}/runs", headers=auth_headers)
        assert history.status_code == 200
        assert len(history.json()) == 1

    def test_edit_preserves_execution_history(self, client, auth_headers):
        auto_id = self._create(client, auth_headers)
        client.post(f"/automation/{auto_id}/run", headers=auth_headers)

        updated = client.put(f"/automation/{auto_id}", json={
            "name": "Renamed",
            "trigger_config": {"time": "09:30"},
        }, headers=auth_headers)
        assert updated.status_code == 200
        assert updated.json()["name"] == "Renamed"
        assert updated.json()["trigger_config"]["time"] == "09:30"
        # Same record (id preserved) → history intact.
        assert updated.json()["id"] == auto_id
        assert len(client.get(f"/automation/{auto_id}/runs", headers=auth_headers).json()) == 1

    def test_edit_rejects_invalid_action(self, client, auth_headers):
        auto_id = self._create(client, auth_headers)
        r = client.put(f"/automation/{auto_id}", json={
            "actions": [{"tool_name": "run_shell", "arguments": {}}],
        }, headers=auth_headers)
        assert r.status_code == 422

    def test_disable_enable_keeps_history(self, client, auth_headers):
        auto_id = self._create(client, auth_headers)
        client.post(f"/automation/{auto_id}/run", headers=auth_headers)

        assert client.post(f"/automation/{auto_id}/disable", headers=auth_headers).json()["enabled"] is False
        enabled = client.post(f"/automation/{auto_id}/enable", headers=auth_headers)
        assert enabled.json()["enabled"] is True
        assert enabled.json()["next_run_at"] is not None
        assert len(client.get(f"/automation/{auto_id}/runs", headers=auth_headers).json()) == 1

    def test_preview_draft_endpoint_validates_without_saving(self, client, auth_headers):
        before = len(client.get("/automation/", headers=auth_headers).json())
        r = client.post("/automation/preview", json={
            "name": "Draft Preview",
            "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "list_tasks", "arguments": {}}],
        }, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["valid"] is True
        assert r.json()["next_run_at"] is not None
        assert len(client.get("/automation/", headers=auth_headers).json()) == before

    def test_preview_draft_rejects_a_bad_tool(self, client, auth_headers):
        r = client.post("/automation/preview", json={
            "name": "Bad Draft",
            "trigger_type": "schedule",
            "trigger_config": {"time": "08:00"},
            "actions": [{"tool_name": "nope_not_real", "arguments": {}}],
        }, headers=auth_headers)
        assert r.status_code == 422


# ──────────────────────────────────────────────────────────────
# 20. Agent integration (automation → agent → tool → service → DB)
# ──────────────────────────────────────────────────────────────

class TestAgentIntegration:

    def _seed(self, allowed_tools=("create_task",), max_steps=5, enabled=True,
              notifications_enabled=False):
        from app.models.agent import AgentDefinitionModel
        from uuid import uuid4

        db = _app_session()
        user = _app_user(db, notifications_enabled=notifications_enabled)
        agent = AgentDefinitionModel(
            id=f"autoagent_{uuid4().hex[:8]}",
            name="Automation Test Agent",
            description="Test agent",
            system_instructions="Create tasks when asked.",
            capabilities=["tasks"],
            allowed_tools=list(allowed_tools),
            memory_policy="none",
            knowledge_access="none",
            max_steps=max_steps,
            max_tool_calls=max_steps,
            timeout_seconds=60.0,
            confirmation_policy="default",
            enabled=enabled,
            is_builtin=False,
            user_id=user.id,
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return db, user, agent

    def _automation_for(self, db, user, agent_id, prompt="Create a task"):
        auto = Automation(
            user_id=user.id,
            name="Agent Automation",
            trigger_type="interval",
            trigger_config={"interval_minutes": 60},
            conditions=[],
            actions=[{
                "tool_name": "run_agent",
                "arguments": {"agent_id": agent_id, "prompt": prompt},
            }],
            timezone="UTC",
            failure_policy="stop",
            enabled=True,
            max_retries=0,
            retry_delay_seconds=0,
        )
        db.add(auto)
        db.commit()
        db.refresh(auto)
        return auto

    def test_automation_runs_agent_which_creates_a_task(self):
        from app.models.task import Task

        db, user, agent = self._seed()
        try:
            auto = self._automation_for(db, user, agent.id)
            llm_replies = [
                {"response": '{"tool_call": {"name": "create_task", "arguments": {"title": "Agent-created task"}}}'},
                {"response": "Done — I created the task."},
            ]
            with patch("app.agents.agent_service.llm_service.generate",
                       side_effect=llm_replies):
                run = ExecutionEngine().execute(auto, db)

            assert run.status == "completed", run.execution_log
            assert run.actions_completed == 1
            titles = [
                t.title for t in db.query(Task).filter(Task.user_id == user.id).all()
            ]
            assert "Agent-created task" in titles
        finally:
            db.close()

    def test_automation_caps_agent_steps(self):
        """A 5-step agent must be held to the stricter automation cap of 3."""
        import itertools
        import json as _json

        from app.models.agent import AgentRunModel

        db, user, agent = self._seed(max_steps=5)
        try:
            auto = self._automation_for(db, user, agent.id)
            counter = itertools.count(1)

            def always_tool_call(prompt, provider):
                # Distinct arguments each step: avoids the repeated-call guard.
                n = next(counter)
                return {"response": _json.dumps({
                    "tool_call": {"name": "list_tasks", "arguments": {"limit": n}}
                })}

            with patch("app.agents.agent_service.llm_service.generate",
                       side_effect=always_tool_call):
                run = ExecutionEngine().execute(auto, db)

            agent_run = (
                db.query(AgentRunModel)
                .filter(AgentRunModel.user_id == user.id)
                .order_by(AgentRunModel.started_at.desc())
                .first()
            )
            assert agent_run is not None
            assert agent_run.status == "limit_reached"
            assert agent_run.current_step == 3, (
                f"agent ran {agent_run.current_step} steps; the automation cap is 3"
            )
            assert run.status == "completed"
        finally:
            db.close()

    def test_agent_tool_allow_list_is_still_enforced(self):
        from app.models.task import Task

        db, user, agent = self._seed(allowed_tools=("list_tasks",))
        try:
            auto = self._automation_for(db, user, agent.id)
            llm_replies = [
                {"response": '{"tool_call": {"name": "create_task", "arguments": {"title": "Not allowed"}}}'},
                {"response": "I could not do that."},
            ]
            with patch("app.agents.agent_service.llm_service.generate",
                       side_effect=llm_replies):
                run = ExecutionEngine().execute(auto, db)

            assert run.status == "completed"
            titles = [
                t.title for t in db.query(Task).filter(Task.user_id == user.id).all()
            ]
            assert "Not allowed" not in titles
        finally:
            db.close()

    def test_disabled_agent_cannot_be_run(self):
        db, user, agent = self._seed(enabled=False)
        try:
            auto = self._automation_for(db, user, agent.id)
            run = ExecutionEngine().execute(auto, db)
            assert run.status == "failed"
            assert "disabled" in (run.execution_log[0].get("error") or "").lower()
        finally:
            db.close()

    def test_another_users_agent_cannot_be_run(self):
        db, owner, agent = self._seed()
        try:
            intruder = _app_user(db)
            auto = self._automation_for(db, intruder, agent.id)
            run = ExecutionEngine().execute(auto, db)
            assert run.status == "failed"
            assert "not found" in (run.execution_log[0].get("error") or "").lower()
        finally:
            db.close()

    def test_run_agent_tool_requires_the_agents_run_permission(self):
        from app.tools.tool_executor import tool_executor as real_executor
        from app.tools.tool_context import ToolExecutionContext

        result = real_executor.execute(
            "run_agent",
            {"agent_id": "productivity_agent", "prompt": "hi"},
            ToolExecutionContext(user_id=1, permissions=["tasks.read"]),
        )
        assert result.success is False
        assert result.error.code.value == "PERMISSION_DENIED"

