from datetime import datetime


class DailyReport:


    def generate(self, analysis, score):

        return {

            "date": datetime.now().strftime(
                "%Y-%m-%d"
            ),

            "completed_tasks": analysis[
                "completed_tasks"
            ],

            "pending_tasks": analysis[
                "pending_tasks"
            ],

            "productivity_score": score[
                "score"
            ],

            "productivity_level": score[
                "level"
            ],

            "message": self.get_message(
                score["score"]
            )
        }


    def get_message(self, score):

        if score >= 80:
            return "Excellent work. Keep the momentum."

        elif score >= 50:
            return "Good progress. Finish remaining tasks."

        else:
            return "Focus on completing important tasks."
