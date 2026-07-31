import importlib
import os


class ToolDiscovery:

    def discover(self):

        tools = []

        path = os.path.dirname(__file__)

        for file in os.listdir(path):

            if file.endswith("_tool.py"):

                module_name = file.replace(".py", "")

                module = importlib.import_module(
                    f"app.tools.{module_name}"
                )

                tools.append(module_name)


        return tools
