from sqlalchemy import Column, Integer, String, Boolean
from backend.app.db import Base

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)