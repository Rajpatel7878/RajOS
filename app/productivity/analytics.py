class ProductivityAnalytics:


    def weekly_analysis(self, history):

        if not history:
            return {
                "total_tasks": 0,
                "completed_tasks": 0,
                "weekly_score": 0,
                "daily_data": []
            }


        total = sum(
            item["total"]
            for item in history
        )


        completed = sum(
            item["completed"]
            for item in history
        )


        score = 0

        if total > 0:
            score = round(
                (completed / total) * 100,
                2
            )


        best_day = max(
            history,
            key=lambda x: x["completion_rate"]
        )


        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": total - completed,
            "weekly_score": score,
            "best_day": best_day["date"],
            "daily_data": history
        }


    def graph_data(self, history):

        return [
            {
                "date": item["date"],
                "completed": item["completed"],
                "total": item["total"],
                "completion_rate": item["completion_rate"]
            }
            for item in history
        ]
