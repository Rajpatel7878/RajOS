class ProductivityScore:


    def calculate(self, progress):

        completion_rate = progress.get(
            "completion_rate",
            0
        )

        priority_bonus = progress.get(
            "priority_bonus",
            0
        )

        deadline_bonus = progress.get(
            "deadline_bonus",
            0
        )


        score = (
            completion_rate
            + priority_bonus
            + deadline_bonus
        )


        if score > 100:
            score = 100


        if score >= 80:
            level = "excellent"

        elif score >= 50:
            level = "good"

        else:
            level = "needs improvement"


        return {
            "score": round(score, 2),
            "level": level
        }
