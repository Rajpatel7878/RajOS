from typing import Any, Dict, List, Optional
from app.tools.tool_definition import ToolDefinition, ToolCategory
from app.tools.task_tools import (
    CreateTaskTool, ListTasksTool, GetTaskTool,
    UpdateTaskTool, CompleteTaskTool, DeleteTaskTool
)
from app.tools.note_tools import (
    CreateNoteTool, ListNotesTool, GetNoteTool,
    UpdateNoteTool, DeleteNoteTool, SearchNotesTool
)
from app.tools.memory_tools import (
    RememberTool, SearchMemoryTool, ForgetMemoryTool
)
from app.tools.knowledge_tools import SearchKnowledgeTool
from app.tools.search_tools import SearchWorkspaceTool


class ToolRegistry:

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

        # Register default starter tool set
        self.register(CreateTaskTool())
        self.register(ListTasksTool())
        self.register(GetTaskTool())
        self.register(UpdateTaskTool())
        self.register(CompleteTaskTool())
        self.register(DeleteTaskTool())

        self.register(CreateNoteTool())
        self.register(ListNotesTool())
        self.register(GetNoteTool())
        self.register(UpdateNoteTool())
        self.register(DeleteNoteTool())
        self.register(SearchNotesTool())

        self.register(RememberTool())
        self.register(SearchMemoryTool())
        self.register(ForgetMemoryTool())

        self.register(SearchKnowledgeTool())
        self.register(SearchWorkspaceTool())

    def register(self, tool: ToolDefinition) -> None:
        if not isinstance(tool, ToolDefinition):
            raise TypeError("Only instances of ToolDefinition can be registered.")
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def exists(self, name: str) -> bool:
        return name in self._tools

    def list_tools(
        self,
        category: Optional[ToolCategory] = None,
        permissions: Optional[List[str]] = None
    ) -> List[ToolDefinition]:
        result = []
        for tool in self._tools.values():
            if not tool.enabled:
                continue
            if category and tool.category != category:
                continue
            if permissions is not None:
                # Check if tool requires permissions user doesn't have
                if tool.required_permissions:
                    has_perm = any(
                        perm in permissions or "*" in permissions or "admin" in permissions
                        for perm in tool.required_permissions
                    )
                    if not has_perm:
                        continue
            result.append(tool)
        return result

    def export_llm_schemas(
        self,
        category: Optional[ToolCategory] = None,
        permissions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        tools = self.list_tools(category=category, permissions=permissions)
        return [tool.to_llm_schema() for tool in tools]


tool_registry = ToolRegistry()
