from datetime import datetime


class ProgressTracker:


    def __init__(self):

        self.history = []


    def record_progress(self, data):

        record = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "completed": data["completed_tasks"],
            "total": data["total_tasks"],
            "completion_rate": data["completion_rate"]
        }

        self.history.append(record)

        return record


    def get_history(self):

        return self.history
