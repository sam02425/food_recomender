from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from backend.app.db import Base

class Participant(Base):
    __tablename__ = 'participants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    responses = Column(JSON, default={})
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Participant(name={self.name}, email={self.email})>"