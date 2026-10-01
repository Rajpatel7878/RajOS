from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.productivity.task_analyzer import task_analyzer
from app.productivity.workload_service import workload_service
from app.productivity.recommendation_engine import recommendation_engine
from app.productivity.planning_service import planning_service


# --- Input Schemas ---

class GetProductivitySummaryInput(BaseModel):
    pass

class GetDailyBriefInput(BaseModel):
    pass

class GetWeeklySummaryInput(BaseModel):
    pass

class GetOverdueTasksInput(BaseModel):
    pass

class GetDueSoonTasksInput(BaseModel):
    pass

class GetTaskRecommendationsInput(BaseModel):
    pass

class PlanTasksInput(BaseModel):
    available_minutes: Optional[int] = Field(None, description="Available focus time in minutes (e.g., 240 for 4 hours)", ge=15, le=1440)
    constraints: Optional[str] = Field(None, description="Optional constraints or preferences for planning")

class BreakDownTaskInput(BaseModel):
    title: str = Field(..., description="Title of the complex task to break down", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Optional detailed task description")

class GetWorkloadInput(BaseModel):
    pass

class GetProductivityTrendsInput(BaseModel):
    pass


# --- Tool Implementations ---

class GetProductivitySummaryTool(ToolDefinition):
    name = "get_productivity_summary"
    description = "Get a comprehensive productivity analysis and status for the authenticated user."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetProductivitySummaryInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return task_analyzer.analyze_user_tasks(db, context.user_id)
        finally:
            db.close()


class GetDailyBriefTool(ToolDefinition):
    name = "get_daily_brief"
    description = "Get today's productivity brief including overdue items, tasks due today, recommended focus, and quick wins."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetDailyBriefInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return workload_service.get_daily_brief(db, context.user_id)
        finally:
            db.close()


class GetWeeklySummaryTool(ToolDefinition):
    name = "get_weekly_summary"
    description = "Get a weekly productivity report of tasks completed, on-time rate, and category workload."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetWeeklySummaryInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return workload_service.get_weekly_summary(db, context.user_id)
        finally:
            db.close()


class GetOverdueTasksTool(ToolDefinition):
    name = "get_overdue_tasks"
    description = "Get all tasks whose due dates have passed and are still incomplete."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetOverdueTasksInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            res = task_analyzer.analyze_user_tasks(db, context.user_id)
            return {"count": len(res["overdue_tasks"]), "overdue_tasks": res["overdue_tasks"]}
        finally:
            db.close()


class GetDueSoonTasksTool(ToolDefinition):
    name = "get_due_soon_tasks"
    description = "Get tasks that are due within the next 3 days."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetDueSoonTasksInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            res = task_analyzer.analyze_user_tasks(db, context.user_id)
            return {"count": len(res["due_soon_tasks"]), "due_soon_tasks": res["due_soon_tasks"]}
        finally:
            db.close()


class GetTaskRecommendationsTool(ToolDefinition):
    name = "get_task_recommendations"
    description = "Get explainable, structured productivity suggestions for what to work on next."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetTaskRecommendationsInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            recs = recommendation_engine.generate_recommendations(db, context.user_id)
            return {"count": len(recs), "recommendations": recs}
        finally:
            db.close()


class PlanTasksTool(ToolDefinition):
    name = "plan_tasks"
    description = "Generate an optimized daily work schedule based on priorities, due dates, and available time."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = PlanTasksInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = PlanTasksInput(**arguments)
        db = SessionLocal()
        try:
            return planning_service.plan_day(
                db=db,
                user_id=context.user_id,
                available_minutes=args.available_minutes,
                constraints=args.constraints
            )
        finally:
            db.close()


class BreakDownTaskTool(ToolDefinition):
    name = "break_down_task"
    description = "Suggest a structured subtask breakdown for a complex task. Does NOT create tasks automatically."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = BreakDownTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = BreakDownTaskInput(**arguments)
        return planning_service.breakdown_task(title=args.title, description=args.description)


class GetWorkloadTool(ToolDefinition):
    name = "get_workload"
    description = "Get workload metrics including category distribution, priority distribution, and total estimated duration."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetWorkloadInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return workload_service.get_workload_analysis(db, context.user_id)
        finally:
            db.close()


class GetProductivityTrendsTool(ToolDefinition):
    name = "get_productivity_trends"
    description = "Get historical 7-day productivity completion trends."
    category = ToolCategory.PRODUCTIVITY
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetProductivityTrendsInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            return workload_service.get_productivity_trends(db, context.user_id)
        finally:
            db.close()
