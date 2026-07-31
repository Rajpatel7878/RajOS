from abc import ABC, abstractmethod


class BaseTool(ABC):

    @abstractmethod
    def execute(self, data):
        pass

    @abstractmethod
    def name(self):
        pass
