class Planner:

    def create_plan(self, user_input: str):

        plan = [
            "Understand user request",
            "Check memory",
            "Search documents",
            "Generate response"
        ]

        return {
            "goal": user_input,
            "steps": plan
        }
