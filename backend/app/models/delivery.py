from sqlalchemy import Column, Integer, String
from backend.app.db import Base

class DeliveryZone(Base):
    __tablename__ = 'delivery_zones'
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String)  # WKT or GeoJSON string for area