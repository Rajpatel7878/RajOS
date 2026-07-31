from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    messages = relationship(
        "Message",
        back_populates="conversation"
    )

    user = relationship(
        "User"
    )
