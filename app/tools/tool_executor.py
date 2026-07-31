class ToolExecutor:

    def execute(
        self,
        tool,
        data=None
    ):

        try:

            result = tool.execute(
                data
            )

            return {
                "status": "success",
                "result": result
            }


        except Exception as error:

            return {
                "status": "failed",
                "error": str(error)
            }
