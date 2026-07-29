class ProductivityScore:


    def calculate(self, progress):

        score = progress.get(
            "completion_rate",
            0
        )


        if score >= 80:
            level = "excellent"

        elif score >= 50:
            level = "good"

        else:
            level = "needs improvement"


        return {
            "score": score,
            "level": level
        }
