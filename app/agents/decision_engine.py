class DecisionEngine:

    def decide(self, message):

        text = message.lower()

        intent = "general"
        action = "respond"
        priority = "normal"


        if any(word in text for word in [
            "create a task",
            "create task",
            "add task",
            "new task",
            "todo",
            "task"
        ]):
            intent = "task_creation"
            action = "create_task"


        elif any(word in text for word in [
            "note",
            "save note",
            "remember"
        ]):
            intent = "note_creation"
            action = "create_note"


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
