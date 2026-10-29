"""Automation Engine 2.0 — Condition Engine.

Evaluates deterministic guard conditions against live user data
WITHOUT invoking any LLM. Conditions are evaluated against a snapshot
of the user's task/note state derived from the database.

Two forms are supported:

  1. A flat list of rules — implicitly AND-ed (backward compatible).
     ``[{"field": "overdue_tasks", "operator": ">", "value": 0}]``

  2. Nested groups for AND / OR / NOT:
     ``[{"op": "and", "rules": [{"field": ..., "operator": ..., "value": ...},
                                {"op": "not", "rules": [...]}]}]``

Group nesting is capped at ``_MAX_GROUP_DEPTH`` so an automation can never
carry an unbounded condition tree.  ``validate()`` rejects anything the
evaluator could not decide deterministically — an unknown field is a hard
error, never a silent "false".
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.task import Task

logger = logging.getLogger(__name__)

# Supported operators
_OPERATORS = ("==", "!=", ">", "<", ">=", "<=", "in", "contains", "not_in")

# Supported group operators
_GROUP_OPERATORS = ("and", "or", "not")

# Maximum nesting depth of condition groups (prevents unbounded trees)
_MAX_GROUP_DEPTH = 3

# Fields that can be evaluated
_SUPPORTED_FIELDS = {
    "overdue_tasks",        # count of tasks past due_date, not completed
    "pending_tasks",        # count of incomplete tasks
    "completed_tasks",      # count of completed tasks
    "total_tasks",          # total task count
    "day_of_week",          # "mon","tue","wed","thu","fri","sat","sun"
    "hour_of_day",          # 0-23 integer
}


class ConditionEngine:
    """Evaluates a list of ConditionRule / ConditionGroup dicts against user data."""

    # ------------------------------------------------------------------
    # Validation (used at automation create/update time)
    # ------------------------------------------------------------------

    def validate(self, conditions: Optional[List[Dict[str, Any]]]) -> None:
        """Raise ValueError when a condition tree is malformed or unsupported."""
        if conditions is None:
            return
        if not isinstance(conditions, list):
            raise ValueError("'conditions' must be a list.")
        self._validate_list(conditions, depth=1)

    def _validate_list(self, rules: List[Any], depth: int) -> None:
        if depth > _MAX_GROUP_DEPTH:
            raise ValueError(
                f"Conditions may not nest more than {_MAX_GROUP_DEPTH} levels deep."
            )
        if not isinstance(rules, list):
            raise ValueError("Each condition group needs a 'rules' list.")
        for rule in rules:
            if not isinstance(rule, dict):
                raise ValueError("Each condition must be an object.")
            if "op" in rule:
                op = str(rule.get("op", "")).lower()
                if op not in _GROUP_OPERATORS:
                    raise ValueError(
                        f"Unsupported condition group operator '{rule.get('op')}'. "
                        f"Expected one of: {sorted(_GROUP_OPERATORS)}."
                    )
                nested = rule.get("rules")
                if not isinstance(nested, list) or not nested:
                    raise ValueError(
                        f"Condition group '{op}' requires a non-empty 'rules' list."
                    )
                self._validate_list(nested, depth + 1)
                continue

            field = rule.get("field")
            if field not in _SUPPORTED_FIELDS:
                raise ValueError(
                    f"Unsupported condition field '{field}'. "
                    f"Expected one of: {sorted(_SUPPORTED_FIELDS)}."
                )
            operator = rule.get("operator", "==")
            if operator not in _OPERATORS:
                raise ValueError(
                    f"Unsupported condition operator '{operator}'. "
                    f"Expected one of: {sorted(_OPERATORS)}."
                )
            if "value" not in rule:
                raise ValueError(
                    f"Condition on '{field}' requires a 'value'."
                )

    # ------------------------------------------------------------------
    # Live data snapshot
    # ------------------------------------------------------------------

    def build_context(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Fetch a lightweight snapshot of user data for condition evaluation.

        The snapshot is strictly scoped to ``user_id`` — conditions can never
        observe another user's data.
        """
        now = datetime.now(timezone.utc)

        tasks = db.query(Task).filter(Task.user_id == user_id).all()

        overdue = sum(
            1 for t in tasks
            if not t.completed
            and t.due_date is not None
            and t.due_date.replace(tzinfo=timezone.utc) < now
        )
        pending = sum(1 for t in tasks if not t.completed)
        completed = sum(1 for t in tasks if t.completed)

        day_map = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        return {
            "overdue_tasks": overdue,
            "pending_tasks": pending,
            "completed_tasks": completed,
            "total_tasks": len(tasks),
            "day_of_week": day_map[now.weekday()],
            "hour_of_day": now.hour,
        }

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        conditions: List[Dict[str, Any]],
        db: Session,
        user_id: int,
        context_override: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Return True if the condition tree passes.

        A flat list is AND-ed.  Groups use "and" / "or" / "not" semantics.
        An empty / missing list is vacuously true.

        Args:
            conditions:       List of rule / group dicts.
            db:               Database session.
            user_id:          Owner to build the data context for.
            context_override: Optionally inject a pre-built context (for testing).
        """
        if not conditions:
            return True  # vacuously true

        try:
            self.validate(conditions)
        except ValueError as exc:
            logger.error("Invalid condition tree rejected at evaluation time: %s", exc)
            return False

        ctx = context_override or self.build_context(db, user_id)
        return self._evaluate_list(conditions, ctx)

    def _evaluate_list(self, rules: List[Dict[str, Any]], ctx: Dict[str, Any]) -> bool:
        """AND semantics for a list of rules / groups."""
        for rule in rules:
            if not self._evaluate_node(rule, ctx):
                return False
        return True

    def _evaluate_node(self, rule: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
        if "op" in rule:
            op = str(rule.get("op", "")).lower()
            rules = rule.get("rules") or []
            if op == "and":
                return self._evaluate_list(rules, ctx)
            if op == "or":
                return any(self._evaluate_node(r, ctx) for r in rules)
            if op == "not":
                return not self._evaluate_list(rules, ctx)
            return False

        field = rule.get("field", "")
        operator = rule.get("operator", "==")
        expected = rule.get("value")

        if field not in ctx:
            logger.warning(
                "Condition field '%s' not supported — treated as False.", field
            )
            return False

        actual = ctx[field]
        try:
            result = self._compare(actual, operator, expected)
        except Exception as exc:
            logger.error(
                "Condition evaluation error for field '%s' op '%s': %s",
                field, operator, exc
            )
            return False

        logger.debug(
            "Condition %s: %s %s %s (actual=%s)",
            "PASSED" if result else "FAILED", field, operator, expected, actual,
        )
        return result

    def _compare(self, actual: Any, operator: str, expected: Any) -> bool:
        """Apply the comparison operator to actual vs expected."""
        if operator == "==":
            return actual == expected
        elif operator == "!=":
            return actual != expected
        elif operator == ">":
            return actual > expected
        elif operator == "<":
            return actual < expected
        elif operator == ">=":
            return actual >= expected
        elif operator == "<=":
            return actual <= expected
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        elif operator == "contains":
            return expected in actual
        else:
            raise ValueError(f"Unsupported operator: '{operator}'")


condition_engine = ConditionEngine()
