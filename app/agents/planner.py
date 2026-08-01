class Planner:

    def create_plan(self, user_input: str, intent="general"):

        plans = {

            "task_creation": [
                "Understand task details",
                "Extract task information",
                "Create task",
                "Confirm completion"
            ],

            "note_creation": [
                "Understand note content",
                "Extract important information",
                "Save note",
                "Confirm storage"
            ],

            "document_management": [
                "Understand document request",
                "Identify requested operation",
                "Process document",
                "Confirm completion"
            ],

            "productivity_analysis": [
                "Collect productivity data",
                "Analyze metrics",
                "Generate productivity insights",
                "Return report"
            ],

            "information_search": [
                "Understand search query",
                "Find relevant information",
                "Rank results",
                "Generate answer"
            ],

            "planning": [
                "Understand goal",
                "Break goal into steps",
                "Create timeline",
                "Provide action plan"
            ],

            "note_reference": [
                "Resolve referenced note",
                "Retrieve note",
                "Generate response"
            ],

            "task_reference": [
                "Resolve referenced task",
                "Retrieve task",
                "Generate response"
            ],

            "general": [
                "Understand user request",
                "Check memory",
                "Process request",
                "Generate response"
            ]
        }

        return {
            "goal": user_input,
            "intent": intent,
            "steps": plans.get(intent, plans["general"])
        }
