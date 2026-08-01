from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.search_history import SearchHistory


class SearchAnalytics:

    @staticmethod
    def top_searches(db: Session):

        return (
            db.query(
                SearchHistory.query,
                func.count(SearchHistory.id).label("count")
            )
            .group_by(SearchHistory.query)
            .order_by(func.count(SearchHistory.id).desc())
            .limit(10)
            .all()
        )
