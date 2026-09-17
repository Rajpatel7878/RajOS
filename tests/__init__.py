"""
RajOS Test Suite
=================

Run with:  pytest tests/ -v
Coverage:  pytest tests/ --cov=app --cov-report=term-missing -v

These tests use an in-memory SQLite database (never touches rajos.db).
No live API keys are required — Gemini/OpenAI calls are not exercised.
"""
