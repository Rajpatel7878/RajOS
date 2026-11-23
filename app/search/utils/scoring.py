"""Deterministic lexical relevance scoring for RajOS unified search.

Everything in this module is pure and synchronous: the same inputs always
produce the same scores.  No LLM or embedding call is performed here.

Ranking strategy (documented in ``docs/RAJOS_V2_UNIFIED_SEARCH.md``):

* title relevance      -> 60% of the lexical score
* body relevance       -> 30%
* keyword coverage     -> 10%
* semantic similarity  -> optional 25% blend when a provider supplies it
* recency              -> at most 3% of the final score

A strong title match therefore always outranks a merely recent result.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, Optional, Sequence

from rapidfuzz import fuzz

MAX_QUERY_LENGTH = 200
MAX_TERMS = 20
MAX_SNIPPET_LENGTH = 240

_WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAG_RE = re.compile(r"<[^>]{1,200}>")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: Optional[str]) -> str:
    """Lower-case and collapse whitespace for case-insensitive comparison."""
    if not value:
        return ""
    return _WHITESPACE_RE.sub(" ", str(value)).strip().lower()


def tokenize_query(query: Optional[str]) -> list[str]:
    """Split a query into unique, bounded, wildcard-free search terms.

    Only alphanumeric/unicode word characters survive, so user input can never
    introduce SQL ``LIKE`` wildcards (``%`` / ``_``) or injection payloads.
    """
    if not query:
        return []

    terms: list[str] = []
    seen: set[str] = set()
    for term in _WORD_RE.findall(normalize_text(query)):
        if len(term) < 2 and len(terms) > 0:
            continue
        if term in seen:
            continue
        seen.add(term)
        terms.append(term)
        if len(terms) >= MAX_TERMS:
            break
    return terms


def sanitize_text(value: Optional[str], limit: Optional[int] = None) -> str:
    """Make untrusted resource text safe and readable for display.

    HTML tags and control characters are removed, whitespace is collapsed and
    the result is truncated.  Callers still render snippets as plain text, so
    this is defence in depth rather than the only protection.
    """
    if not value:
        return ""
    text = _CONTROL_RE.sub(" ", str(value))
    text = _HTML_TAG_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    if limit is not None and len(text) > limit:
        text = text[: max(0, limit - 1)].rstrip() + "…"
    return text


def build_snippet(text: Optional[str], query: str, terms: Sequence[str], length: int = MAX_SNIPPET_LENGTH) -> str:
    """Return a short, sanitized window of text centred on the first match."""
    cleaned = sanitize_text(text)
    if not cleaned:
        return ""

    haystack = cleaned.lower()
    position = -1
    for candidate in [normalize_text(query), *terms]:
        if not candidate:
            continue
        found = haystack.find(candidate)
        if found != -1 and (position == -1 or found < position):
            position = found

    if position == -1 or len(cleaned) <= length:
        return cleaned[:length].rstrip()

    start = max(0, position - (length // 3))
    end = min(len(cleaned), start + length)

    # Avoid cutting words where possible.
    if start > 0:
        space = cleaned.find(" ", start)
        if 0 <= space < position:
            start = space + 1
    if end < len(cleaned):
        space = cleaned.rfind(" ", start, end)
        if space > start:
            end = space

    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(cleaned) else ""
    return f"{prefix}{cleaned[start:end].strip()}{suffix}"


def matched_fields(fields: Dict[str, Optional[str]], terms: Sequence[str]) -> list[str]:
    """Report which named fields contain at least one query term."""
    matches: list[str] = []
    for name, value in fields.items():
        haystack = normalize_text(value)
        if not haystack:
            continue
        if any(term in haystack for term in terms):
            matches.append(name)
    return matches


def _text_match_score(text: str, query: str, terms: Sequence[str]) -> float:
    """Score how well one text field matches the query (0.0 - 1.0)."""
    if not text or not query:
        return 0.0

    if text == query:
        return 1.0
    if text.startswith(query):
        return 0.94
    if query in text:
        return 0.88

    if terms and all(term in text for term in terms):
        return 0.74

    matched_terms = sum(1 for term in terms if term in text)
    if matched_terms:
        coverage = matched_terms / len(terms)
        return min(0.68, 0.30 + (0.38 * coverage))

    # Typo tolerance is deliberately limited so unrelated text never scores.
    ratio = fuzz.partial_ratio(query, text) / 100.0
    if ratio >= 0.78:
        return round(0.30 * ratio, 4)
    return 0.0


@dataclass(frozen=True)
class LexicalScore:
    """Transparent breakdown of a deterministic lexical score."""

    title: float
    body: float
    coverage: float
    combined: float


def score_lexical(title: Optional[str], body_fields: Iterable[Optional[str]], query: str) -> LexicalScore:
    """Score a resource using title matches first, then body matches."""
    query_norm = normalize_text(query)
    terms = tokenize_query(query)
    title_norm = normalize_text(title)
    body_norm = normalize_text(" ".join(value for value in body_fields if value))

    if not query_norm or not terms:
        return LexicalScore(0.0, 0.0, 0.0, 0.0)

    title_score = _text_match_score(title_norm, query_norm, terms)
    body_score = _text_match_score(body_norm, query_norm, terms)

    haystack = f"{title_norm} {body_norm}"
    coverage = sum(1 for term in terms if term in haystack) / len(terms)

    combined = (0.60 * title_score) + (0.30 * body_score) + (0.10 * coverage)
    return LexicalScore(
        title=round(title_score, 4),
        body=round(body_score, 4),
        coverage=round(coverage, 4),
        combined=round(min(1.0, max(0.0, combined)), 4),
    )


def recency_score(updated_at: Optional[datetime], now: Optional[datetime] = None) -> float:
    """Exponential recency in the 0..1 range (half-life: 180 days)."""
    if updated_at is None:
        return 0.0
    now = now or datetime.utcnow()
    age_seconds = max(0.0, (now - updated_at).total_seconds())
    age_days = age_seconds / 86400.0
    return round(math.pow(0.5, age_days / 180.0), 4)


def combine_scores(
    lexical: float,
    semantic: Optional[float],
    recency: float,
) -> float:
    """Blend lexical, optional semantic and small recency signals.

    Semantic scores are only blended in when a provider actually produced one;
    lexical-only providers are never penalised for missing embeddings.
    """
    lexical = min(1.0, max(0.0, lexical))

    if semantic is None:
        text_score = lexical
    else:
        semantic = min(1.0, max(0.0, semantic))
        text_score = (0.75 * lexical) + (0.25 * semantic)

    final = (0.97 * text_score) + (0.03 * min(1.0, max(0.0, recency)))
    return round(min(1.0, final), 4)
