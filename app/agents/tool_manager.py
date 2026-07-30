class ToolManager:

    def select_tool(self, user_input: str):

        text = user_input.lower()

        if any(word in text for word in [
            "note",
            "notes",
            "save note",
            "create note",
            "add note",
            "write note",
            "show note",
            "show notes",
            "list notes",
            "my notes"
        ]):
            return "notes"

        if any(word in text for word in [
            "task",
            "tasks",
            "todo",
            "complete task"
        ]):
            return "tasks"

        if any(word in text for word in [
            "memory",
            "remember"
        ]):
            return "memory"

        if any(word in text for word in [
            "document",
            "documents",
            "pdf",
            "file"
        ]):
            return "documents"

        if any(word in text for word in [
            "productive",
            "productivity",
            "progress",
            "daily report",
            "weekly report"
        ]):
            return "productivity"

        return None
