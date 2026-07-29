from app.tools.tasks_tool import TasksTool
from app.tools.notes_tool import NotesTool
from app.tools.memory_tool import MemoryTool
from app.tools.document_tool import DocumentTool
from app.tools.productivity_tool import ProductivityTool


class ToolRegistry:

    def __init__(self):

        self.tools = {}

        self.register(TasksTool())
        self.register(NotesTool())
        self.register(MemoryTool())
        self.register(DocumentTool())
        self.register(ProductivityTool())


    def register(self, tool):

        self.tools[
            tool.name()
        ] = tool


    def list_tools(self):

        return list(
            self.tools.keys()
        )


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
