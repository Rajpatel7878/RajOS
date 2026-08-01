from app.tools.base_tool import BaseTool
from app.memory.memory_engine import MemoryEngine


class MemoryTool(BaseTool):

    def __init__(self):
        self.engine = MemoryEngine()

    def name(self):
        return "memory"

    def execute(self, data):

        try:

            result = self.engine.process_memory(
                data["message"]
                if isinstance(data, dict)
                else data
            )

            return {
                "tool": self.name(),
                "status": "success",
                "memories_saved": result
            }

        except Exception as e:

            return {
                "tool": self.name(),
                "status": "error",
                "message": str(e)
            }
