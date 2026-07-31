from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    role = Column(String, nullable=False)

    content = Column(String, nullable=False)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id")
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )
