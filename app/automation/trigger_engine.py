from app.automation.workflow_engine import workflow_engine


class TriggerEngine:


    def check_trigger(
        self,
        trigger: str,
        event: dict
    ):

        event_type = event.get(
            "type"
        )


        if trigger != event_type:

            return {
                "status": "ignored",
                "message": "Trigger does not match"
            }


        return {
            "status": "triggered",
            "trigger": trigger,
            "event": event
        }



    def execute_trigger(
        self,
        automation,
        event: dict
    ):

        result = self.check_trigger(
            automation.trigger,
            event
        )


        if result["status"] != "triggered":

            return result



        workflow_result = workflow_engine.execute(
            automation.action,
            event
        )


        return {
            "trigger_result": result,
            "workflow_result": workflow_result
        }



trigger_engine = TriggerEngine()
