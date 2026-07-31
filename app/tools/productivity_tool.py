from app.tools.base_tool import BaseTool

from app.productivity.task_analyzer import TaskAnalyzer
from app.productivity.productivity_score import ProductivityScore
from app.notifications.notification_manager import NotificationManager


class ProductivityTool(BaseTool):


    def name(self):

        return "productivity"


    def execute(self, data):

        analyzer = TaskAnalyzer()
        scorer = ProductivityScore()
        notifier = NotificationManager()


        analysis = analyzer.analyze()


        score = scorer.calculate(
            analysis
        )


        notification = None


        user = data.get("user")


        if analysis["pending_tasks"] > 0 and user:

            notification = notifier.send_task_reminder(
                user,
                f"You have {analysis['pending_tasks']} tasks remaining today"
            )


        return {
            "tool": self.name(),
            "analysis": analysis,
            "score": score,
            "user_received": user is not None,
            "notification": notification
        }
