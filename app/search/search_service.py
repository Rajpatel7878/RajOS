"""Backwards-compatible import path for the unified search engine.

The legacy ``SearchService`` used to search every resource inside one method,
without authentication or user scoping.  It now delegates to
:class:`app.search.unified_search_service.UnifiedSearchService` so there is a
single search implementation in RajOS.
"""

from app.search.unified_search_service import UnifiedSearchService, unified_search_service


class SearchService(UnifiedSearchService):
    """Deprecated alias kept so existing imports keep working."""
