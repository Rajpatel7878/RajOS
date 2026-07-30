from sqlalchemy.orm import Session
from app.models.preference import UserPreference

class PreferenceManager:

    def save_preference(self, db: Session, user_id: int, key: str, value: str):
        preference = db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.key == key
        ).first()

        if preference:
            preference.value = value
        else:
            preference = UserPreference(
                user_id=user_id,
                key=key,
                value=value
            )
            db.add(preference)

        db.commit()
        db.refresh(preference)
        return preference

    def get_preference(self, db: Session, user_id: int, key: str):
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.key == key
        ).first()

    def get_all_preferences(self, db: Session, user_id: int):
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()

    def delete_preference(self, db: Session, user_id: int, key: str):
        preference = self.get_preference(db, user_id, key)

        if preference:
            db.delete(preference)
            db.commit()
            return True

        return False
