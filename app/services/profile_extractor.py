class ProfileExtractor:


    def extract(self, message):

        text = message.lower()


        if "my name is" in text:

            name = text.split(
                "my name is"
            )[1].strip()
            name = name.title()

            return {
                "key": "name",
                "value": name
            }


        if "i use" in text and "python" in text:

            return {
                "key": "language",
                "value": "Python"
            }


        return None
