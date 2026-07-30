from sqlalchemy.orm import Session
from app.models.preference import UserPreference

class PreferenceQuery:

    def get_preference(self, db: Session, user_id: int, key: str):
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.key == key
        ).first()

        if preference:
            return preference.value

        return None

    def get_all_preferences(self, db: Session, user_id: int):
        prefs = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()

        return {
            p.key: p.value
            for p in prefs
        }
