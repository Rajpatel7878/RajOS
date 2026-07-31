from app.services.profile_service import ProfileService


class ProfileQuery:

    def __init__(self):
        self.service = ProfileService()


    def get_profile(
        self,
        db,
        user_id,
        key
    ):

        profile = self.service.get(
            db,
            user_id,
            key
        )

        if profile:
            return profile.value

        return None
