from sqlalchemy import Column, Integer, String, ForeignKey

from app.database.connection import Base


class UserProfile(Base):

    __tablename__ = "user_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    key = Column(
        String,
        nullable=False
    )

    value = Column(
        String,
        nullable=False
    )
