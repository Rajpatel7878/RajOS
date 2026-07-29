class Executor:

    def execute(self, plan: dict):

        completed = []

        for step in plan["steps"]:
            completed.append(f"Completed: {step}")

        return {
            "goal": plan["goal"],
            "completed_steps": completed,
            "status": "Execution completed"
        }
