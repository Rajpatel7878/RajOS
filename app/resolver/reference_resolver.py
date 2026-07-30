class ReferenceResolver:


    def resolve(self, message, context=None):

        context = context or {}

        if "context" in context:
            context = context["context"]



        text = message.lower()


        result = {
            "has_reference": False,
            "entity": None,
            "type": None
        }


        reference_words = [
            "it",
            "that",
            "this",
            "previous",
            "last one",
            "show"
        ]


        if any(word in text for word in reference_words):

            result["has_reference"] = True


            last_entity = context.get("last_entity")
            last_intent = context.get("last_intent")


            if last_entity:
                result["entity"] = last_entity


            if last_intent == "note":
                result["type"] = "note"

            elif last_intent == "task":
                result["type"] = "task"

            elif last_intent == "document":
                result["type"] = "document"


        return result
