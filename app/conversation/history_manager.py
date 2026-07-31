class HistoryManager:

    def __init__(self):
        self.history = []

    def add(self, message):
        self.history.append(message)

    def get(self):
        return self.history
