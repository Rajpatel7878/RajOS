class ConversationEngine:

    def process(self, message, context=None):

        context = context or {}

        text = message.lower()

        last_intent = context.get("last_intent")
        last_entity = context.get("last_entity")

        response = f"RajOS understood: {message}"

        if any(word in text for word in [
            "it",
            "that",
            "this",
            "them"
        ]):

            if last_intent and last_entity:

                response = (
                    f"I believe you're referring to your previous "
                    f"{last_intent}:\n\n{last_entity}"
                )

            else:

                response = (
                    "I'm not sure what you're referring to. "
                    "Could you please clarify?"
                )

        return {
            "input": message,
            "context": context,
            "response": response
        }
