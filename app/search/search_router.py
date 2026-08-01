from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.search.search_service import SearchService
from app.search.search_models import SearchResult

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

@router.get("/", response_model=SearchResult)
def search(
    q: str,
    page: int = 1,
    limit: int = 10,
    type: str = "all",
    db: Session = Depends(get_db),
):
    return SearchService.search(
        db=db,
        query=q,
        page=page,
        limit=limit,
        search_type=type,
    )
