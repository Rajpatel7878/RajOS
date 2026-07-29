from app.tools.notes_tool import NotesTool
from app.tools.tasks_tool import TasksTool
from app.tools.memory_tool import MemoryTool
from app.tools.document_tool import DocumentTool


class ToolRegistry:

    def __init__(self):

        self.tools = {
            "notes": NotesTool(),
            "tasks": TasksTool(),
            "memory": MemoryTool(),
            "documents": DocumentTool(),
        }

    def get_tool(self, name):

        return self.tools.get(name)

    def execute(self, name, data):

        tool = self.get_tool(name)

        if tool is None:
            return {
                "status": "error",
                "message": f"Tool '{name}' not found"
            }

        return tool.execute(data)
