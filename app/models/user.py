from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String, unique=True)

    email = Column(String, unique=True)

    password = Column(String)

    tasks = relationship(
        "Task",
        back_populates="user"
    )

    notes = relationship(
        "Note",
        back_populates="user"
    )

    memories = relationship(
        "Memory",
        back_populates="user"
    )
