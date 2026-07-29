from app.tools.base_tool import BaseTool

from app.productivity.task_analyzer import TaskAnalyzer
from app.productivity.productivity_score import ProductivityScore


class ProductivityTool(BaseTool):


    def name(self):

        return "productivity"


    def execute(self, data):

        analyzer = TaskAnalyzer()
        scorer = ProductivityScore()


        analysis = analyzer.analyze()

        score = scorer.calculate(
            analysis
        )


        return {
            "tool": self.name(),
            "analysis": analysis,
            "score": score
        }
