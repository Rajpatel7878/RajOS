class ToolManager:

    def select_tool(self, user_input: str):

        text = user_input.lower()


        if any(word in text for word in [
            "note",
            "save note"
        ]):
            return "notes"


        if any(word in text for word in [
            "task",
            "todo"
        ]):
            return "tasks"


        if any(word in text for word in [
            "memory",
            "remember"
        ]):
            return "memory"


        if any(word in text for word in [
            "document",
            "pdf",
            "file"
        ]):
            return "documents"


        return None
