from sqlalchemy.orm import Session

from app.models.profile import UserProfile


class ProfileService:


    def save(
        self,
        db: Session,
        user_id,
        key,
        value
    ):

        profile = UserProfile(
            user_id=user_id,
            key=key,
            value=value
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile


    def get(
        self,
        db: Session,
        user_id,
        key
    ):

        return db.query(
            UserProfile
        ).filter(
            UserProfile.user_id == user_id,
            UserProfile.key == key
        ).first()
