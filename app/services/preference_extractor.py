class PreferenceExtractor:

    def extract(self, message: str):
        text = message.lower()

        if "dark mode" in text:
            return ("theme", "dark")

        if "light mode" in text:
            return ("theme", "light")

        if "short answers" in text or "short answer" in text:
            return ("response_style", "short")

        if "detailed answers" in text or "detailed answer" in text:
            return ("response_style", "detailed")

        if "preferred language is" in text:
            value = message.split("preferred language is", 1)[1].strip()
            return ("language", value)

        return None
