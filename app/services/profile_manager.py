from app.services.profile_service import ProfileService
from app.services.profile_extractor import ProfileExtractor


class ProfileManager:

    def __init__(self):
        self.service = ProfileService()
        self.extractor = ProfileExtractor()


    def process(
        self,
        db,
        user_id,
        message
    ):

        profile = self.extractor.extract(
            message
        )

        if profile:

            return self.service.save(
                db,
                user_id,
                profile["key"],
                profile["value"]
            )

        return None
