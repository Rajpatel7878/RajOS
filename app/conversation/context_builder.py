class ContextBuilder:


    def build(self, user_id, history=None):

        history = history or []

        last_message = history[-1] if history else None

        last_intent = None
        last_entity = None


        for message in reversed(history):

            text = message.lower()


            if "note" in text:

                last_intent = "note"
                last_entity = message
                break


            elif "task" in text:

                last_intent = "task"
                last_entity = message
                break


            elif any(word in text for word in [
                "document",
                "pdf",
                "file"
            ]):

                last_intent = "document"
                last_entity = message
                break


            elif any(word in text for word in [
                "memory",
                "remember"
            ]):

                last_intent = "memory"
                last_entity = message
                break


        return {
            "user_id": user_id,
            "history": history,
            "last_message": last_message,
            "last_intent": last_intent,
            "last_entity": last_entity
        }
