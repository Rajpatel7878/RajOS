from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.note import Note
from app.models.memory import Memory
from app.models.conversation import Conversation
from app.models.search_history import SearchHistory

from app.search.search_models import SearchResult
from app.search.utils.ranking import calculate_score
from app.search.utils.highlight import highlight


class SearchService:

    @staticmethod
    def search(
        db: Session,
        query: str,
        page: int = 1,
        limit: int = 10,
        search_type: str = "all",
    ) -> SearchResult:

        history = SearchHistory(
            query=query,
            search_type=search_type
        )

        db.add(history)
        db.commit()

        offset = (page - 1) * limit

        tasks = []
        notes = []
        memories = []
        conversations = []

        if search_type in ("all", "tasks"):
            tasks = db.query(Task).filter(
                Task.title.ilike(f"%{query}%")
            ).all()

            tasks.sort(
                key=lambda x: calculate_score(x.title, query),
                reverse=True
            )

            for item in tasks:
                item.title = highlight(item.title, query)

            tasks = tasks[offset:offset+limit]


        if search_type in ("all", "notes"):
            notes = db.query(Note).filter(
                Note.title.ilike(f"%{query}%")
            ).all()

            notes.sort(
                key=lambda x: calculate_score(x.title, query),
                reverse=True
            )

            for item in notes:
                item.title = highlight(item.title, query)

            notes = notes[offset:offset+limit]


        if search_type in ("all", "memories"):
            memories = db.query(Memory).filter(
                Memory.value.ilike(f"%{query}%")
            ).all()

            memories.sort(
                key=lambda x: calculate_score(x.value, query),
                reverse=True
            )

            for item in memories:
                item.value = highlight(item.value, query)

            memories = memories[offset:offset+limit]


        if search_type in ("all", "conversations"):
            conversations = db.query(Conversation).filter(
                Conversation.title.ilike(f"%{query}%")
            ).all()

            conversations.sort(
                key=lambda x: calculate_score(x.title or "", query),
                reverse=True
            )

            for item in conversations:
                if item.title:
                    item.title = highlight(item.title, query)

            conversations = conversations[offset:offset+limit]


        total = (
            len(tasks)
            + len(notes)
            + len(memories)
            + len(conversations)
        )

        return SearchResult(
            tasks=tasks,
            notes=notes,
            memories=memories,
            conversations=conversations,
            documents=[],
            total_results=total,
            page=page,
            limit=limit,
        )
