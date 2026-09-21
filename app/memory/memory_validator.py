import re
from typing import Tuple


class MemoryValidator:
    """
    Validates memory candidates to filter out sensitive credentials, API keys,
    passwords, temporary commands, and low-quality conversational noise.
    """

    SECRET_PATTERNS = [
        re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|bearer\s+[A-Za-z0-9\-\._~\+\/]+=*)'),
        re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*\S+'),
        re.compile(r'(?i)(db[_-]?pass|database[_-]?password|postgres://|mysql://|mongodb\+srv://)'),
        re.compile(r'ghp_[A-Za-z0-9]{36}'),  # GitHub Personal Access Token
        re.compile(r'sk-[A-Za-z0-9]{32,}'),  # OpenAI API Key
        re.compile(r'AIzaSy[A-Za-z0-9\-_]{33}'),  # Google API Key
        re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # SSN
        re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b')  # Credit card
    ]

    TEMPORARY_NOISE_PATTERNS = [
        re.compile(r'^(hi|hello|hey|greetings|good morning|good evening|howdy|what\'s up)\b', re.I),
        re.compile(r'^(what time is it|what is the time|current time|today\'s date|weather today)\b', re.I),
        re.compile(r'^(thanks|thank you|ok|okay|cool|got it|awesome|great)\b', re.I),
        re.compile(r'^(run|execute|open|close|start|stop|restart|show|list)\s+cmd\b', re.I),
        re.compile(r'^(clear screen|reset chat|delete message)\b', re.I)
    ]

    @classmethod
    def validate(cls, key: str, value: str, content: str = "") -> Tuple[bool, str]:
        """
        Validates key, value, and optional content.
        Returns (is_valid, reason).
        """
        full_text = f"{key} {value} {content}".strip()

        if not key or not key.strip() or len(key.strip()) < 2:
            return False, "Key is too short or empty."

        if not value or not value.strip() or len(value.strip()) < 2:
            return False, "Value is too short or empty."

        # Check for secrets
        for pattern in cls.SECRET_PATTERNS:
            if pattern.search(full_text):
                return False, "Memory rejected: Contains sensitive credentials, secrets, or financial data."

        # Check for temporary noise
        for pattern in cls.TEMPORARY_NOISE_PATTERNS:
            if pattern.search(value.strip()) or pattern.search(key.strip()):
                return False, "Memory rejected: Transient context or conversational noise."

        return True, "Valid"


memory_validator = MemoryValidator()
