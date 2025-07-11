from sqlalchemy import Column, Integer, String
from backend.app.db import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    hours = Column(String, nullable=False)

    def __repr__(self):
        return f"<Location(name={self.name}, address={self.address})>"
