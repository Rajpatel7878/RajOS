from fastapi import APIRouter

from app.productivity.task_analyzer import TaskAnalyzer
from app.productivity.productivity_score import ProductivityScore
from app.productivity.daily_report import DailyReport


router = APIRouter(
    prefix="/productivity",
    tags=["Productivity"]
)


@router.get("/daily")
def daily_report():

    analyzer = TaskAnalyzer()
    scorer = ProductivityScore()
    report = DailyReport()


    analysis = analyzer.analyze()

    score = scorer.calculate(
        analysis
    )

    return report.generate(
        analysis,
        score
    )


@router.get("/score")
def productivity_score():

    analyzer = TaskAnalyzer()
    scorer = ProductivityScore()


    analysis = analyzer.analyze()

    return scorer.calculate(
        analysis
    )
@router.get("/weekly")
def weekly_report():

    return {
        "week": {
            "total_tasks": 40,
            "completed_tasks": 32,
            "pending_tasks": 8
        },
        "productivity_score": 80,
        "message": "Weekly productivity calculated"
    }



@router.get("/graph")
def productivity_graph():

    return {
        "labels": [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"
        ],
        "completed_tasks": [
            5,
            7,
            4,
            8,
            6,
            2,
            9
        ],
        "pending_tasks": [
            2,
            1,
            4,
            0,
            3,
            5,
            1
        ]
    }
