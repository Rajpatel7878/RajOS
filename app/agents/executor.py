class Executor:

    def execute(self, plan: dict):

        completed = []
        failed = []

        for step in plan.get("steps", []):

            try:
                completed.append({
                    "step": step,
                    "status": "completed"
                })

            except Exception as error:
                failed.append({
                    "step": step,
                    "error": str(error)
                })


        return {
            "goal": plan.get("goal"),
            "intent": plan.get("intent", "general"),
            "completed_steps": completed,
            "failed_steps": failed,
            "status": "Execution completed"
        }
