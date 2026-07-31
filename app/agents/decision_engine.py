class DecisionEngine:

    def decide(self, message):

        text = message.lower()

        intent = "general"
        action = "respond"
        priority = "normal"

        if any(word in text for word in [
            "create task",
            "create a task",
            "add task",
            "new task",
            "todo",
            "task"
        ]):
            intent = "task_creation"
            action = "create_task"

        elif any(word in text for word in [
            "note",
            "notes",
            "save note",
            "create note",
            "add note",
            "remember"
        ]):
            intent = "note_creation"
            action = "create_note"

        elif any(word in text for word in [
            "document",
            "documents",
            "pdf",
            "upload document",
            "create document",
            "search document",
            "list documents",
            "show documents",
            "file"
        ]):
            intent = "document_management"
            action = "manage_document"

        elif any(word in text for word in [
            "productive",
            "productivity",
            "daily report",
            "weekly report",
            "progress"
        ]):
            intent = "productivity_analysis"
            action = "analyze_productivity"

        elif any(word in text for word in [
            "search",
            "find"
        ]):
            intent = "information_search"
            action = "search"

        elif any(word in text for word in [
            "plan",
            "schedule"
        ]):
            intent = "planning"
            action = "create_plan"

        return {
            "intent": intent,
            "action": action,
            "priority": priority
        }
