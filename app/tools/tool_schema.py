class ToolSchema:

    def __init__(
        self,
        name: str,
        description: str,
        actions: list
    ):

        self.name = name
        self.description = description
        self.actions = actions


    def info(self):

        return {
            "name": self.name,
            "description": self.description,
            "actions": self.actions
        }
