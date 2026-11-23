"""Task search provider."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy.orm import Session

from app.models.task import Task
from app.search.providers.base import ProviderHit, ProviderQuery, SearchProvider, contains_any


class TaskSearchProvider(SearchProvider):
    resource_type = "tasks"
    display_name = "Tasks"
    default_url = "/tasks"

    def search(self, db: Session, user_id: int, query: ProviderQuery, limit: int) -> List[ProviderHit]:
        condition = contains_any(
            [Task.title, Task.description, Task.category, Task.tags],
            query.terms,
        )
        if condition is None:
            return []

        q = db.query(Task).filter(Task.user_id == user_id, condition)
        if query.date_from is not None:
            q = q.filter(Task.updated_at >= query.date_from)
        if query.date_to is not None:
            q = q.filter(Task.updated_at <= query.date_to)

        tasks = (
            q.order_by(Task.updated_at.desc(), Task.id.desc())
            .limit(min(limit, self.candidate_limit))
            .all()
        )

        hits: List[ProviderHit] = []
        for task in tasks:
            fields: Dict[str, Any] = {
                "title": task.title,
                "description": task.description,
                "category": task.category,
                "tags": task.tags,
            }
            hit = self.make_hit(
                resource_id=task.id,
                title=task.title,
                snippet_source=task.description or task.title,
                query=query,
                fields=fields,
                created_at=task.created_at,
                updated_at=task.updated_at,
                metadata={
                    "completed": bool(task.completed),
                    "priority": task.priority,
                    "category": task.category,
                },
            )
            if hit.matched_fields:
                hits.append(hit)
        return hits

    def suggest(
        self, db: Session, user_id: int, query: str, terms: Sequence[str], limit: int
    ) -> List[Dict[str, Any]]:
        condition = contains_any([Task.title], terms)
        if condition is None:
            return []
        rows = (
            db.query(Task.id, Task.title)
            .filter(Task.user_id == user_id, condition)
            .order_by(Task.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "text": row.title,
                "kind": "resource",
                "resource_type": self.resource_type,
                "resource_id": str(row.id),
                "url": self.default_url,
            }
            for row in rows
        ]
