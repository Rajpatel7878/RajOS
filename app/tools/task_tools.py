from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.tools.tool_definition import ToolDefinition, ToolCategory, RiskLevel
from app.tools.tool_context import ToolExecutionContext
from app.database.connection import SessionLocal
from app.models.task import Task


# --- Pydantic Argument Schemas ---

class CreateTaskInput(BaseModel):
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Optional detailed task description")
    priority: Optional[str] = Field("normal", description="Priority level: low, normal, high")

    @validator("priority")
    def validate_priority(cls, v):
        if v and v.lower() not in ["low", "normal", "high"]:
            raise ValueError("Priority must be one of: low, normal, high")
        return v.lower() if v else "normal"


class ListTasksInput(BaseModel):
    completed: Optional[bool] = Field(None, description="Filter tasks by completion status")
    limit: Optional[int] = Field(50, description="Max number of tasks to return", ge=1, le=100)


class GetTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to retrieve", ge=1)


class UpdateTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to update", ge=1)
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    priority: Optional[str] = Field(None, description="New priority: low, normal, high")
    completed: Optional[bool] = Field(None, description="Mark completed or pending")

    @validator("priority")
    def validate_priority(cls, v):
        if v and v.lower() not in ["low", "normal", "high"]:
            raise ValueError("Priority must be one of: low, normal, high")
        return v.lower() if v else None


class CompleteTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to mark as complete", ge=1)


class DeleteTaskInput(BaseModel):
    task_id: int = Field(..., description="ID of the task to delete", ge=1)


# --- Tool Implementations ---

class CreateTaskTool(ToolDefinition):
    name = "create_task"
    description = "Create a new task for the authenticated user."
    category = ToolCategory.TASKS
    read_only = False
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.write"]
    args_model = CreateTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = CreateTaskInput(**arguments)
        db = SessionLocal()
        try:
            task = Task(
                title=args.title,
                description=args.description,
                priority=args.priority,
                completed=False,
                user_id=context.user_id
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            return {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        finally:
            db.close()


class ListTasksTool(ToolDefinition):
    name = "list_tasks"
    description = "List all tasks belonging to the authenticated user."
    category = ToolCategory.TASKS
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = ListTasksInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = ListTasksInput(**arguments)
        db = SessionLocal()
        try:
            query = db.query(Task).filter(Task.user_id == context.user_id)
            if args.completed is not None:
                query = query.filter(Task.completed == args.completed)
            tasks = query.order_by(Task.id.desc()).limit(args.limit).all()
            return {
                "count": len(tasks),
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "priority": t.priority,
                        "completed": t.completed,
                        "created_at": t.created_at.isoformat() if t.created_at else None
                    }
                    for t in tasks
                ]
            }
        finally:
            db.close()


class GetTaskTool(ToolDefinition):
    name = "get_task"
    description = "Get details of a specific task by its ID."
    category = ToolCategory.TASKS
    read_only = True
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.read"]
    args_model = GetTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = GetTaskInput(**arguments)
        db = SessionLocal()
        try:
            task = db.query(Task).filter(
                Task.id == args.task_id,
                Task.user_id == context.user_id
            ).first()
            if not task:
                raise ValueError(f"Task with ID {args.task_id} was not found.")
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        finally:
            db.close()


class UpdateTaskTool(ToolDefinition):
    name = "update_task"
    description = "Update an existing task."
    category = ToolCategory.TASKS
    read_only = False
    risk_level = RiskLevel.MEDIUM
    requires_confirmation = False
    required_permissions = ["tasks.write"]
    args_model = UpdateTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = UpdateTaskInput(**arguments)
        db = SessionLocal()
        try:
            task = db.query(Task).filter(
                Task.id == args.task_id,
                Task.user_id == context.user_id
            ).first()
            if not task:
                raise ValueError(f"Task with ID {args.task_id} was not found.")
            if args.title is not None:
                task.title = args.title
            if args.description is not None:
                task.description = args.description
            if args.priority is not None:
                task.priority = args.priority
            if args.completed is not None:
                task.completed = args.completed
                if args.completed:
                    task.completed_at = datetime.utcnow()
                else:
                    task.completed_at = None

            db.commit()
            db.refresh(task)
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
        finally:
            db.close()


class CompleteTaskTool(ToolDefinition):
    name = "complete_task"
    description = "Mark a task as completed."
    category = ToolCategory.TASKS
    read_only = False
    risk_level = RiskLevel.LOW
    requires_confirmation = False
    required_permissions = ["tasks.write"]
    args_model = CompleteTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = CompleteTaskInput(**arguments)
        db = SessionLocal()
        try:
            task = db.query(Task).filter(
                Task.id == args.task_id,
                Task.user_id == context.user_id
            ).first()
            if not task:
                raise ValueError(f"Task with ID {args.task_id} was not found.")
            task.completed = True
            task.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            return {
                "id": task.id,
                "title": task.title,
                "completed": task.completed
            }
        finally:
            db.close()


class DeleteTaskTool(ToolDefinition):
    name = "delete_task"
    description = "Delete a task by ID. Requires user confirmation."
    category = ToolCategory.TASKS
    read_only = False
    risk_level = RiskLevel.HIGH
    requires_confirmation = True
    required_permissions = ["tasks.write"]
    args_model = DeleteTaskInput

    def execute(self, arguments: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        args = DeleteTaskInput(**arguments)
        db = SessionLocal()
        try:
            task = db.query(Task).filter(
                Task.id == args.task_id,
                Task.user_id == context.user_id
            ).first()
            if not task:
                raise ValueError(f"Task with ID {args.task_id} was not found.")
            deleted_title = task.title
            db.delete(task)
            db.commit()
            return {
                "task_id": args.task_id,
                "deleted_title": deleted_title,
                "status": "deleted"
            }
        finally:
            db.close()
