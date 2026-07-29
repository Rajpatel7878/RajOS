class ToolManager:

    def select_tool(self, user_input: str):

        text = user_input.lower()

        if "note" in text:
            return "notes"

        if "task" in text:
            return "tasks"

        if "memory" in text:
            return "memory"

        if "document" in text or "pdf" in text:
            return "documents"

        return "chat"
