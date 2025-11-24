from sqlalchemy import Column, Integer, String
from common.db.connection import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    equipment = Column(String, nullable=False)
    location = Column(String, nullable=False)   # <-- ADD THIS
